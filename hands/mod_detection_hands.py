# detection_hands in moduli per fittare in screen4
import cv2
import os
import time
import threading
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class HandTrackerGeneral:
    def __init__(self):
        self.modello_path = "hand_landmarker.task"
        self._check_model()
        
        # Inizializzazione del rilevatore MediaPipe
        base_options = python.BaseOptions(model_asset_path=self.modello_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        self.running = False
        self.thread = None
        self.tempo_mani = 0.0

    def _check_model(self):
        if not os.path.exists(self.modello_path):
            print("[BACKEND] Download del modello MediaPipe per le mani...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, self.modello_path)

    def _loop_rilevamento(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERRORE] Impossibile accedere alla webcam per il tracciamento mani.")
            self.running = False
            return

        tempo_precedente = time.time()

        while self.running:
            successo, frame = cap.read()
            if not successo:
                continue

            tempo_attuale = time.time()
            delta_time = tempo_attuale - tempo_precedente
            tempo_precedente = tempo_attuale

            # Ottimizzazione e conversione per MediaPipe
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            
            timestamp_ms = int(time.time() * 1000)
            risultati = self.detector.detect_for_video(mp_image, timestamp_ms)

            # Se le mani sono visibili, incrementa il cronometro relativo alla risposta
            if risultati.hand_landmarks:
                self.tempo_mani += delta_time

        cap.release()

    def start(self):
        """Azzera il cronometro e avvia il tracciamento in background"""
        self.tempo_mani = 0.0
        self.running = True
        self.thread = threading.Thread(target=self._loop_rilevamento, daemon=True)
        self.thread.start()
        print(">>> [ANALISI VISIVA] Tracciamento mani avviato.")

    def stop(self):
        """Ferma il tracciamento e restituisce i secondi accumulati"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print(f">>>> [ANALISI VISIVA] Tracciamento mani fermato. Tempo: {self.tempo_mani:.1f}s")
        return self.tempo_mani
    


def process_and_print_gesture_analysis(session_results):
    """
    Prende i risultati della sessione e stampa il report 
    relativo al comportamento visivo e alla gesticolazione.
    """
    print("\n" + "="*50)
    print("GESTURE ANALYSIS IN PROGRESS... PLEASE WAIT")
    print("="*50)
    
    for result in session_results:
        question = result["question"]
        tempo_mani = result.get("hand_general_time", 0.0)
        
        print(f"\nQUESTION: {question}")
        print(f"  > Gesticulation Time: {tempo_mani:.1f} seconds")
        
        # Feedback comportamentale basato sul tempo di gesticolazione
        if tempo_mani == 0:
            print("      [Feedback: Nessun gesto rilevato. Usa le mani per enfatizzare i concetti importanti.]")
        elif tempo_mani < 4.0:
            print("      [Feedback: Gesticolazione moderata e controllata. Ottimo bilanciamento.]")
        else:
            print("      [Feedback: Gesticolazione molto energica. Attenzione a non distrarre l'intervistatore.]")
            
        print("-" * 30)