#funziona bene per destra e sinistra
# NON FUNZIONA PER SU E GIU (MA TANTO CI VA LA TESTA PER SU E GIU, NO?)
import cv2
import urllib.request
import os
import time
import math
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

def calcola_distanza(punto1, punto2):
    # Calcola la distanza tra due punti (x,y) usando il teorema di Pitagora
    return math.hypot(punto2[0] - punto1[0], punto2[1] - punto1[1])

detector_viso = vision.FaceLandmarker.create_from_options(options_viso)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Errore: webcam non trovata.")
    exit()

print("Sistema avviato. Premi 'q' per uscire.")
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
        
        # Disegno dei punti del viso per feedback visivo
        for lm in face_landmarks:
            cx = int(lm.x * w_frame)
            cy = int(lm.y * h_frame)
            cv2.circle(frame, (cx, cy), 1, (255, 0, 0), -1)

        # 1. Estrazione dei 6 punti 2D chiave
        indices = [1, 152, 33, 263, 61, 291]
        face_2d = []
        for idx in indices:
            lm = face_landmarks[idx]
            x, y = int(lm.x * w_frame), int(lm.y * h_frame)
            face_2d.append([x, y])
            
        face_2d = np.array(face_2d, dtype=np.float64)

        # 2. Configurazione della matrice della fotocamera (Intrinsics)
        focal_length = 1 * w_frame  # Approssimazione della distanza focale
        cam_matrix = np.array([
            [focal_length, 0, w_frame / 2], # c_x è il centro sull'asse X (larghezza)
            [0, focal_length, h_frame / 2], # c_y è il centro sull'asse Y (altezza)
            [0, 0, 1]
])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        # 3. Calcolo PnP per trovare rotazione e traslazione 
        # ALGORITMO Perspective-n-Point
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d_model, face_2d, cam_matrix, dist_matrix)
        if success:
            # 4. Conversione del vettore di rotazione in angoli di Eulero
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

            pitch = angles[0]  # Su / Giù
            yaw = angles[1]    # Destra / Sinistra
            roll = angles[2]   # Inclinazione laterale

            # --- INIZIO LOGICA TRACCIAMENTO SGUARDO ---
            # Estrazione dei punti dell'occhio sinistro (33, 133) e iride (468)
            p_esterno = (int(face_landmarks[33].x * w_frame), int(face_landmarks[33].y * h_frame))
            p_interno = (int(face_landmarks[133].x * w_frame), int(face_landmarks[133].y * h_frame))
            p_iride = (int(face_landmarks[468].x * w_frame), int(face_landmarks[468].y * h_frame))

            # Disegno i punti per feedback visivo (Verde per i bordi, Giallo per l'iride)
            cv2.circle(frame, p_esterno, 2, (0, 255, 0), -1)
            cv2.circle(frame, p_interno, 2, (0, 255, 0), -1)
            cv2.circle(frame, p_iride, 2, (0, 255, 255), -1)

            # Calcolo delle distanze
            dist_centro_interno = calcola_distanza(p_iride, p_interno)
            dist_esterno_centro = calcola_distanza(p_esterno, p_iride)

            # Evito la divisione per zero in caso di chiusura totale dell'occhio
            if dist_esterno_centro == 0:
                dist_esterno_centro = 0.01

            gaze_ratio = dist_centro_interno / dist_esterno_centro

            # Analisi del contatto visivo
            stato_sguardo = "Contatto Visivo"
            colore_sguardo = (0, 255, 0)

            # Soglie generiche da testare e calibrare (dipendono dalla forma dell'occhio)
            if gaze_ratio < 0.6:
                stato_sguardo = "Sguardo a Sinistra"
                colore_sguardo = (0, 0, 255)
            elif gaze_ratio > 1.4:
                stato_sguardo = "Sguardo a Destra"
                colore_sguardo = (0, 0, 255)

            # Mostro i dati a schermo
            cv2.putText(frame, f"Sguardo: {stato_sguardo}", (20, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colore_sguardo, 2)
            cv2.putText(frame, f"Gaze Ratio: {gaze_ratio:.2f}", (20, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            # --- FINE LOGICA TRACCIAMENTO SGUARDO ---
    condizione_soddisfatta = False
    colore_interfaccia = (0, 255, 0) if condizione_soddisfatta else (0, 0, 255)
    cv2.imshow("Movimento Viso", frame)

    # Gestione uscita
    tasto = cv2.waitKey(1) & 0xFF
    if tasto == ord("q"):
        running = False


cap.release()
cv2.destroyAllWindows()
detector_viso.close()

