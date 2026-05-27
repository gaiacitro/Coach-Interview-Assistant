#counting seconds the hands are shown as gesticulation
import cv2
import urllib.request
import os
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- 1. DOWNLOAD DEL MODELLO ---
modello_path = "hand_landmarker.task"

if not os.path.exists(modello_path):
    print("Sto scaricando il file dell'IA per le mani...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, modello_path)

# --- 2. CONFIGURAZIONE MEDIAPIPE ---
base_options = python.BaseOptions(model_asset_path=modello_path)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

detector = vision.HandLandmarker.create_from_options(options)

# --- 3. CONFIGURAZIONE WEBCAM ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Errore: webcam non trovata.")
    exit()

print("Sistema avviato. Premi 'q' per uscire.")
running = True

tempo_mani = 0.0
tempo_precedente = time.time()

# --- 4. CICLO PRINCIPALE ---
while running:
    successo, frame = cap.read()
    if not successo:
        continue

    # Calcolo del delta_time reale
    tempo_attuale = time.time()
    delta_time = tempo_attuale - tempo_precedente
    tempo_precedente = tempo_attuale


    # Specchia il frame (effetto specchio) e converti i colori per MediaPipe
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb
    )

    # Calcola il timestamp in millisecondi (richiesto da MediaPipe in modalità VIDEO)
    timestamp_ms = int(time.time() * 1000)
    risultati = detector.detect_for_video(mp_image, timestamp_ms)

    # --- 5. DISEGNO DEI PUNTI (LANDMARKS) ---
    if risultati.hand_landmarks:
        for hand_landmarks in risultati.hand_landmarks:
            for lm in hand_landmarks:
                # Calcola le coordinate in pixel relative alla grandezza del frame
                cx = int(lm.x * frame.shape[1])
                cy = int(lm.y * frame.shape[0])
                
                # Disegna un cerchio verde per ogni punto della mano
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
    
    
    # --- 7. LOGICA DEL CONFRONTO E CRONOMETRO ---
    condizione_soddisfatta = False

    if risultati.hand_landmarks:

        tempo_mani += delta_time
        condizione_soddisfatta = True

    # --- 8. GRAFICA E TIMER A SCHERMO ---
    colore_interfaccia = (0, 255, 0) if condizione_soddisfatta else (0, 0, 255)
    stato_testo = "MANI VISIBILI" if condizione_soddisfatta else "MANI BASSE"
    
    cv2.putText(frame, f"Tempo Area Viso: {tempo_mani:.1f} s", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, colore_interfaccia, 2)
    # --- 6. MOSTRA LA FINESTRA ---
    # Questo è il comando che mancava nel tuo codice originale per vedere il video!
    cv2.imshow("Tracciamento Mani - Base", frame)

    # --- 7. USCITA ---
    tasto = cv2.waitKey(1) & 0xFF
    if tasto == ord("q"):
        running = False

# Pulizia finale
cap.release()
cv2.destroyAllWindows()