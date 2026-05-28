#ROLL=rotazione testa verso la spalla OK
#YAW=movimento destra sinistra orizzontale QUASI OK
#PITCH=movimento su giu della testa verticale OK

import cv2
import os
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

modello_viso_path = "face_landmarker.task"
if not os.path.exists(modello_viso_path):
    print(f"Errore: Il file del modello del viso '{modello_viso_path}' non è stato trovato.")
    exit()

# Coordinate 3D di riferimento per un volto generico
face_3d_model = np.array([
    (0.0, 0.0, 0.0),            # Punta del naso (Landmark 1)
    (0.0, -330.0, -65.0),       # Mento (Landmark 152)
    (-225.0, 170.0, -135.0),    # Angolo occhio sinistro (Landmark 33)
    (225.0, 170.0, -135.0),     # Angolo occhio destro (Landmark 263)
    (-150.0, -150.0, -125.0),   # Angolo bocca sinistro (Landmark 61)
    (150.0, -150.0, -125.0)     # Angolo bocca destro (Landmark 291)
], dtype=np.float64)

base_options_viso = python.BaseOptions(model_asset_path=modello_viso_path)
options_viso = vision.FaceLandmarkerOptions(
    base_options=base_options_viso,
    running_mode=vision.RunningMode.VIDEO,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_face_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

detector_viso = vision.FaceLandmarker.create_from_options(options_viso)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Errore: webcam non trovata.")
    exit()

print("Sistema avviato. Premi 'q' per uscire.")

# --- VARIABILI PER LA CALIBRAZIONE ---
calibrating = True
calibration_duration = 3.0 # Durata in secondi
calibration_start_time = time.time()

# Accumulatori per calcolare la media
pitch_sum = 0
yaw_sum = 0
roll_sum = 0
calibration_frames = 0

# Valori di base (offset)
baseline_pitch = 0
baseline_yaw = 0
baseline_roll = 0
# -------------------------------------

running = True

while running:
    successo, frame = cap.read()
    if not successo:
        continue
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    h_frame, w_frame, _ = frame.shape

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb
    )
    timestamp_ms = int(time.time() * 1000)
    risultati_viso = detector_viso.detect_for_video(mp_image, timestamp_ms)

    if risultati_viso.face_landmarks:
        face_landmarks = risultati_viso.face_landmarks[0]
        
        for lm in face_landmarks:
            cx = int(lm.x * w_frame)
            cy = int(lm.y * h_frame)
            cv2.circle(frame, (cx, cy), 1, (255, 0, 0), -1)

        indices = [1, 152, 33, 263, 61, 291]
        face_2d = []
        for idx in indices:
            lm = face_landmarks[idx]
            x, y = int(lm.x * w_frame), int(lm.y * h_frame)
            face_2d.append([x, y])
            
        face_2d = np.array(face_2d, dtype=np.float64)

        focal_length = 1 * w_frame
        cam_matrix = np.array([
            [focal_length, 0, w_frame / 2],
            [0, focal_length, h_frame / 2],
            [0, 0, 1]
        ])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d_model, face_2d, cam_matrix, dist_matrix)
        if success:
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

            raw_pitch = angles[0]
            raw_yaw = angles[1]
            raw_roll = angles[2]
            
            # Normalizzazione
            if raw_pitch < -90:
                raw_pitch += 180
            elif raw_pitch > 90:
                raw_pitch -= 180
            
            # Normalizzazione
            if raw_roll < -90:
                raw_roll += 180
            elif raw_roll > 90:
                raw_roll -= 180

            # --- GESTIONE CALIBRAZIONE ---
            current_time = time.time()
            elapsed_time = current_time - calibration_start_time
            
            if calibrating:
                if elapsed_time < calibration_duration:
                    tempo_rimasto = int(calibration_duration - elapsed_time) + 1
                    
                    # Raccogliamo i dati SOLO nell'ultimo secondo (quando elapsed_time è tra 2.0 e 3.0)
                    if elapsed_time >= (calibration_duration - 1.0):
                        pitch_sum += raw_pitch
                        yaw_sum += raw_yaw
                        roll_sum += raw_roll
                        calibration_frames += 1
                        messaggio = "Acquisizione zero in corso..."
                    else:
                        messaggio = f"Preparati... {tempo_rimasto}s"
                    
                    # Interfaccia grafica durante la calibrazione
                    cv2.putText(frame, messaggio, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(frame, "Guarda dritto verso la webcam!", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    # Fine dei 3 secondi: calcoliamo le medie sfruttando SOLO i frame dell'ultimo secondo
                    if calibration_frames > 0:
                        baseline_pitch = pitch_sum / calibration_frames
                        baseline_yaw = yaw_sum / calibration_frames
                        baseline_roll = roll_sum / calibration_frames
                    
                    calibrating = False
                    print(f"Calibrazione completata su {calibration_frames} frame dell'ultimo secondo! Baseline impostata.")
            else:
                # --- MODALITÀ NORMALE (Post-Calibrazione) ---
                # Sottraiamo la baseline per far partire gli angoli da zero
                pitch = raw_pitch - baseline_pitch
                yaw = raw_yaw - baseline_yaw
                roll = raw_roll - baseline_roll

                stato_testa = "Frontale"
                
                # Le tue soglie potrebbero aver bisogno di un leggero 
                # aggiustamento ora che partono esattamente da 0.
                if pitch > 13: 
                    stato_testa = "Guarda in basso"
                elif pitch < -18:
                    stato_testa = "Guarda in alto"
                    
                if yaw > 30 or roll <-20:
                    stato_testa = "Guarda a Sinistra"
                elif yaw < -30 or roll>20 :
                    stato_testa = "Guarda a Destra"

            

                # Interfaccia a regime
                cv2.putText(frame, f"Stato: {stato_testa}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Pitch: {int(pitch)}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Yaw: {int(yaw)}", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"Roll: {int(roll)}", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Movimento Viso", frame)

    tasto = cv2.waitKey(1) & 0xFF
    if tasto == ord("q"):
        running = False

cap.release()
cv2.destroyAllWindows()
detector_viso.close()