# hands_movements.py
import cv2
import os
import time
import threading
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class FaceTouchTracker:
    def __init__(self):
        self.modello_mani_path = "hand_landmarker.task"
        self.modello_viso_path = "face_landmarker.task"
        self._check_models()
        
        # --- CONFIGURAZIONE MEDIAPIPE ---
        base_options_mani = python.BaseOptions(model_asset_path=self.modello_mani_path)
        base_options_viso = python.BaseOptions(model_asset_path=self.modello_viso_path)

        options_mani = vision.HandLandmarkerOptions(
            base_options=base_options_mani,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

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

        self.detector_mani = vision.HandLandmarker.create_from_options(options_mani)
        self.detector_viso = vision.FaceLandmarker.create_from_options(options_viso)
        
        self.running = False
        self.thread = None
        self.tempo_mani_sopra_mento = 0.0

    def _check_models(self):
        """Verifica e scarica i modelli se non sono presenti"""
        if not os.path.exists(self.modello_mani_path):
            print("[BACKEND] Scaricamento del modello mani...")
            url_mani = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url_mani, self.modello_mani_path)
            
        if not os.path.exists(self.modello_viso_path):
            print("[BACKEND] Scaricamento del modello viso...")
            url_viso = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            urllib.request.urlretrieve(url_viso, self.modello_viso_path)

    def _loop_rilevamento(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERRORE] Webcam non trovata per il tracciamento del viso e delle mani.")
            self.running = False
            return

        tempo_precedente = time.time()

        while self.running:
            successo, frame = cap.read()
            if not successo:
                continue

            # Calcolo del delta_time reale
            tempo_attuale = time.time()
            delta_time = tempo_attuale - tempo_precedente
            tempo_precedente = tempo_attuale

            # Ottimizzazione frame
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h_frame, w_frame, _ = frame.shape

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int(time.time() * 1000)
            
            # Rilevamento simultaneo
            risultati_mani = self.detector_mani.detect_for_video(mp_image, timestamp_ms)
            risultati_viso = self.detector_viso.detect_for_video(mp_image, timestamp_ms)

            y_mento = None
            pt_mano_piu_alta = None
            min_y_mano = float('inf')

            # Rilevamento Mento
            if risultati_viso.face_landmarks:
                face_landmarks = risultati_viso.face_landmarks[0]
                lm_mento = face_landmarks[152] # Punto del mento
                y_mento = int(lm_mento.y * h_frame)

            # Rilevamento Mano più alta
            if risultati_mani.hand_landmarks:
                for hand_landmarks in risultati_mani.hand_landmarks:
                    for lm in hand_landmarks:
                        cy = int(lm.y * h_frame)
                        cx = int(lm.x * w_frame)
                        if cy < min_y_mano:
                            min_y_mano = cy
                            pt_mano_piu_alta = (cx, cy)

            # Logica di confronto (Senza disegno a schermo)
            if y_mento is not None and pt_mano_piu_alta is not None:
                if pt_mano_piu_alta[1] < y_mento:
                    self.tempo_mani_sopra_mento += delta_time

        cap.release()

    def start(self):
        """Avvia il tracciamento dei tocchi al volto in background"""
        self.tempo_mani_sopra_mento = 0.0
        self.running = True
        self.thread = threading.Thread(target=self._loop_rilevamento, daemon=True)
        self.thread.start()
        print(">>> [ANALISI VISIVA] Tracciamento insicurezza (mani sul viso) avviato.")

    def stop(self):
        """Ferma il tracciamento e restituisce i secondi accumulati"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print(f">>>> [ANALISI VISIVA] Tracciamento insicurezza fermato. Tempo: {self.tempo_mani_sopra_mento:.1f}s")
        return self.tempo_mani_sopra_mento


# --- FUNZIONE DI ANALISI SEPARATA (Ex Passo 3) ---
def process_and_print_insecurity_analysis(session_results):
    """
    Prende i risultati della sessione e stampa il report 
    relativo ai segni di insicurezza (mani vicino al viso).
    """
    print("\n" + "="*50)
    print("INSECURITY & COMFORT ANALYSIS IN PROGRESS...")
    print("="*50)
    
    for result in session_results:
        question = result["question"]
        tempo_viso = result.get("face_touch_time", 0.0)
        
        print(f"\nQUESTION: {question}")
        print(f"  > Hands Near Face/Chin Time: {tempo_viso:.1f} seconds")
        
        """ Feedback sul linguaggio del corpo  FACCIO IOOOOO """
        
        if tempo_viso == 0:
            print("      [Feedback: Ottimo! Postura delle mani sicura, nessun tocco difensivo del volto.]")
        elif tempo_viso < 3.0:
            print("      [Feedback: Qualche tocco sporadico al viso, naturale espressione di riflessione.]")
        else:
            print("      [Feedback: Rilevato tempo prolungato delle mani sul viso. Può comunicare ansia, stress o insicurezza.]")
            
        print("-" * 30)