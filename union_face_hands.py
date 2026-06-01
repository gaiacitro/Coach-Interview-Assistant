
import cv2
import os
import time
import math
import threading
import urllib.request
import numpy as np
from collections import deque
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class UnifiedVisionTracker:
    def __init__(self):
        self.modello_mani_path = "hand_landmarker.task"
        self.modello_viso_path = "face_landmarker.task"
        self._check_models()
        
        # --- CONFIGURAZIONE MEDIAPIPE ---
        base_options_mani = python.BaseOptions(model_asset_path=self.modello_mani_path)
        base_options_viso = python.BaseOptions(model_asset_path=self.modello_viso_path)

        self.detector_mani = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=base_options_mani, running_mode=vision.RunningMode.VIDEO, num_hands=2,
                min_hand_detection_confidence=0.5, min_hand_presence_confidence=0.5, min_tracking_confidence=0.5
            )
        )

        self.detector_viso = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=base_options_viso, running_mode=vision.RunningMode.VIDEO,
                output_face_blendshapes=False, output_facial_transformation_matrixes=False, num_faces=1,
                min_face_detection_confidence=0.5, min_face_presence_confidence=0.5, min_tracking_confidence=0.5
            )
        )
        
        # Modello 3D generico di un volto per algoritmo PnP
        self.face_3d_model = np.array([
            (0.0, 0.0, 0.0),            # Punta del naso (Landmark 1)
            (0.0, -330.0, -65.0),       # Mento (Landmark 152)
            (-225.0, 170.0, -135.0),    # Angolo occhio sinistro (Landmark 33)
            (225.0, 170.0, -135.0),     # Angolo occhio destro (Landmark 263)
            (-150.0, -150.0, -125.0),   # Angolo bocca sinistro (Landmark 61)
            (150.0, -150.0, -125.0)     # Angolo bocca destro (Landmark 291)
        ], dtype=np.float64)
        
        self.running = False
        self.thread = None
        
        # Buffer temporali per il calcolo del tremolio
        self.storico_pitch = deque(maxlen=30)
        self.storico_yaw = deque(maxlen=30)
        self.storico_roll = deque(maxlen=30)

        # Configurazione Calibrazione
        self.calibrating = True
        self.calibration_duration = 3.0
        self.calibration_start_time = 0
        self.pitch_sum = 0
        self.yaw_sum = 0
        self.roll_sum = 0
        self.calibration_frames = 0
        self.baseline_pitch = 0
        self.baseline_yaw = 0
        self.baseline_roll = 0

        # --- ORA ABBIAMO 6 CRONOMETRI ---
        self.tempo_totale = 0.0 
        self.tempo_gesticolazione = 0.0
        self.tempo_mani_sopra_mento = 0.0
        self.tempo_sovrapposizione_box = 0.0
        self.tempo_occhi_girati = 0.0
        self.tempo_instabilita_viso = 0.0
        self.tempo_testa_spostata = 0.0 # <--- NUOVA METRICA DA FACE_MOVEMENTS
        self.tempo_bassa_testa=0.0

    def _check_models(self):
        if not os.path.exists(self.modello_mani_path):
            urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", self.modello_mani_path)
        if not os.path.exists(self.modello_viso_path):
            urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task", self.modello_viso_path)

    def _loop_rilevamento(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.running = False
            return

        tempo_precedente = time.time()

        while self.running:
            successo, frame = cap.read()
            if not successo:
                continue
            self.tempo_totale += delta_time # tempo totale calcolo
            tempo_attuale = time.time()
            delta_time = tempo_attuale - tempo_precedente
            tempo_precedente = tempo_attuale

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h_frame, w_frame, _ = frame.shape

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int(time.time() * 1000)
            
            risultati_mani = self.detector_mani.detect_for_video(mp_image, timestamp_ms)
            risultati_viso = self.detector_viso.detect_for_video(mp_image, timestamp_ms)

            # 1. METRICA GESTICOLAZIONE
            if risultati_mani.hand_landmarks:
                self.tempo_gesticolazione += delta_time

            y_mento = None
            area_box_viso = None
            min_y_mano = float('inf')
            tocco_box_rilevato = False

            if risultati_viso.face_landmarks:
                face_landmarks = risultati_viso.face_landmarks[0]
                y_mento = int(face_landmarks[152].y * h_frame)
                
                # Calcolo Box Espansa (Mani sul viso)
                xs = [int(lm.x * w_frame) for lm in face_landmarks]
                ys = [int(lm.y * h_frame) for lm in face_landmarks]
                min_x, max_x = min(xs), max(xs)
                larghezza_viso = max_x - min_x
                margine_orecchie = int(larghezza_viso * 0.15)
                area_box_viso = (max(0, min_x - margine_orecchie), min(ys), min(w_frame, max_x + margine_orecchie), max(ys))

                # 2. METRICA EYE TRACKING
                p_esterno = (int(face_landmarks[33].x * w_frame), int(face_landmarks[33].y * h_frame))
                p_interno = (int(face_landmarks[133].x * w_frame), int(face_landmarks[133].y * h_frame))
                p_iride = (int(face_landmarks[468].x * w_frame), int(face_landmarks[468].y * h_frame))
                
                dist_centro_interno = math.hypot(p_iride[0] - p_interno[0], p_iride[1] - p_interno[1])
                dist_esterno_centro = math.hypot(p_esterno[0] - p_iride[0], p_esterno[1] - p_iride[1])
                if dist_esterno_centro == 0: dist_esterno_centro = 0.01
                
                gaze_ratio = dist_centro_interno / dist_esterno_centro
                if gaze_ratio < 0.6 or gaze_ratio > 1.4:
                    self.tempo_occhi_girati += delta_time

                # 3. ALGORITMO PnP & ANGOLI DI EULERO (TESTA)
                indices = [1, 152, 33, 263, 61, 291]
                face_2d = np.array([[int(face_landmarks[idx].x * w_frame), int(face_landmarks[idx].y * h_frame)] for idx in indices], dtype=np.float64)
                
                focal_length = w_frame
                cam_matrix = np.array([[focal_length, 0, w_frame / 2], [0, focal_length, h_frame / 2], [0, 0, 1]])
                dist_matrix = np.zeros((4, 1), dtype=np.float64)
                
                success, rot_vec, _ = cv2.solvePnP(self.face_3d_model, face_2d, cam_matrix, dist_matrix)
                if success:
                    rmat, _ = cv2.Rodrigues(rot_vec)
                    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
                    raw_pitch, raw_yaw, raw_roll = angles[0], angles[1], angles[2]

                    # Normalizzazione angoli grezzi
                    if raw_roll < -90: raw_roll += 180
                    elif raw_roll > 90: raw_roll -= 180
                    if raw_pitch < -90: raw_pitch += 180
                    elif raw_pitch > 90: raw_pitch -= 180

                    # --- GESTIONE CALIBRAZIONE ---
                    elapsed_time = time.time() - self.calibration_start_time
                    if self.calibrating:
                        if elapsed_time < self.calibration_duration:
                            if elapsed_time >= (self.calibration_duration - 1.0):
                                self.pitch_sum += raw_pitch
                                self.yaw_sum += raw_yaw
                                self.roll_sum += raw_roll
                                self.calibration_frames += 1
                        else:
                            if self.calibration_frames > 0:
                                self.baseline_pitch = self.pitch_sum / self.calibration_frames
                                self.baseline_yaw = self.yaw_sum / self.calibration_frames
                                self.baseline_roll = self.roll_sum / self.calibration_frames
                            self.calibrating = False
                    else:
                        # Modalità Live: Angoli depurati dalla baseline
                        pitch = raw_pitch - self.baseline_pitch
                        yaw = raw_yaw - self.baseline_yaw
                        roll = raw_roll - self.baseline_roll

                        self.storico_pitch.append(pitch)
                        self.storico_yaw.append(yaw)
                        self.storico_roll.append(roll)

                        # 4. METRICA TREMOLIO VISO
                        if len(self.storico_yaw) == 30:
                            if np.std(self.storico_yaw) > 15 or np.std(self.storico_pitch) > 15:
                                self.tempo_instabilita_viso += delta_time

                        # 5. NUOVA LOGICA COMPORTAMENTALE ORIENTAMENTO TESTA (Le tue nuove soglie esatte)
                        if pitch > 13: 
                            stato_testa = "Guarda in Basso"
                        elif pitch > 7: 
                            if yaw > 30 or roll <-20:
                                stato_testa = "Guarda in Basso"
                            elif yaw < -30 or roll>20 :
                                stato_testa = "Guarda in Basso"
                        elif pitch < -18:
                            stato_testa = "Guarda in alto"
                        elif yaw > 30 or roll <-20:
                                stato_testa = "Guarda a Sinistra"
                        elif yaw < -30 or roll>20 :
                                stato_testa = "Guarda a Destra"


                        # Se lo stato della testa non è più frontale, accumulo il tempo
                        if stato_testa != "Frontale":
                            self.tempo_testa_spostata += delta_time

                        if stato_testa== "Guarda in Basso":
                            self.tempo_bassa_testa+=delta_time

            # Controllo geometrico delle mani
            if risultati_mani.hand_landmarks:
                for hand_landmarks in risultati_mani.hand_landmarks:
                    for lm in hand_landmarks:
                        cx, cy = int(lm.x * w_frame), int(lm.y * h_frame)
                        if cy < min_y_mano: min_y_mano = cy
                        if area_box_viso and not tocco_box_rilevato:
                            if area_box_viso[0] <= cx <= area_box_viso[2] and area_box_viso[1] <= cy <= area_box_viso[3]:
                                tocco_box_rilevato = True

                # 6. METRICA MANI SOPRA IL MENTO
                if y_mento is not None and min_y_mano < y_mento:
                    self.tempo_mani_sopra_mento += delta_time
                
                # 7. METRICA SOVRAPPOSIZIONE BOUNDING BOX
                if tocco_box_rilevato:
                    self.tempo_sovrapposizione_box += delta_time

        cap.release()

    def start(self):
        self.tempo_gesticolazione = 0.0
        self.tempo_mani_sopra_mento = 0.0
        self.tempo_sovrapposizione_box = 0.0
        self.tempo_occhi_girati = 0.0
        self.tempo_instabilita_viso = 0.0
        self.tempo_testa_spostata = 0.0 # Reset
        self.tempo_totale = 0.0 
        self.tempo_bassa_testa=0.0
        
        self.pitch_sum = 0
        self.yaw_sum = 0
        self.roll_sum = 0
        self.calibration_frames = 0
        self.storico_pitch.clear()
        self.storico_yaw.clear()
        self.storico_roll.clear()
        
        self.calibrating = True
        self.calibration_start_time = time.time()
        
        self.running = True
        self.thread = threading.Thread(target=self._loop_rilevamento, daemon=True)
        self.thread.start()
        print(">>> [ANALISI INTEGRATA] Webcam attiva. Analisi visiva completa avviata con nuove soglie.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # Impacchettiamo i dati CV direttamente qui!
        cv_data_dict = {
            "gaze_face": {
                "tempo_totale_risposta": self.tempo_totale,
                "eye_gaze_time": self.tempo_occhi_girati,
                "face_tremor_time": self.tempo_instabilita_viso,
                "head_movement_time": self.tempo_testa_spostata,
                "head_down": self.tempo_bassa_testa,
                "head_total":( 0.5*(self.tempo_bassa_testa)**2+0.5*self.tempo_testa_spostata)/max(self.tempo_totale, 0.1)
            },
            "hand_gesture": {
                "tempo_totale_risposta": self.tempo_totale,
                "hand_general_time": self.tempo_gesticolazione,
                "face_touch_time": self.tempo_mani_sopra_mento-self.tempo_sovrapposizione_box,
                "face_overlap_time": self.tempo_sovrapposizione_box,
                "hand_gravity":( 0.6*(self.tempo_gesticolazione-self.tempo_mani_sopra_mento) + 
                                0.8*(self.tempo_mani_sopra_mento-self.tempo_sovrapposizione_box) + 0.3*(self.tempo_sovrapposizione_box)**2 )/max(self.tempo_totale, 0.1)
            }
        }
        return cv_data_dict


def process_and_print_vision_report(session_results):
    print("\n" + "="*50)
    print("COMPLETE VISUAL BODY LANGUAGE REPORT")
    print("="*50)
    
    for result in session_results:
        print(f"\nQUESTION: {result['question']}")
        print(f"  > Gesticulation Time: {result.get('hand_general_time', 0.0):.1f}s")
        print(f"  > Hands Above Chin Time: {result.get('face_touch_time', 0.0):.1f}s")
        print(f"  > Face Overlap Time (Box): {result.get('face_overlap_time', 0.0):.1f}s")
        print(f"  > Hand Gesture Gravity: {result.get('hand_gravity', 0.0):.1f}s")
        print(f"  > Eyes Distracted Time: {result.get('eye_gaze_time', 0.0):.1f}s")
        print(f"  > Face Tremor/Tension Time: {result.get('face_tremor_time', 0.0):.1f}s")
        print(f"  > Head Moved/Turned Time: {result.get('head_movement_time', 0.0):.1f}s") # <--- AGGIUNTO NEL REPORT
        print("-" * 30)