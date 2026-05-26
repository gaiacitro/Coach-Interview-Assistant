#traking seconds hands touch the face as sign of insecurity
import cv2
import urllib.request
import os
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- 1. CONFIGURAZIONE PERCORSI MODELLI ---
modello_mani_path = "hand_landmarker.task"
if not os.path.exists(modello_mani_path):
    print("Sto scaricando il file dell'IA per le mani...")
    url_mani = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url_mani, modello_mani_path)

modello_viso_path = "face_landmarker.task"
if not os.path.exists(modello_viso_path):
    print(f"Errore: Il file del modello del viso '{modello_viso_path}' non è stato trovato.")
    exit()

# --- 2. CONFIGURAZIONE MEDIAPIPE ---
base_options_mani = python.BaseOptions(model_asset_path=modello_mani_path)
base_options_viso = python.BaseOptions(model_asset_path=modello_viso_path)

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

detector_mani = vision.HandLandmarker.create_from_options(options_mani)
detector_viso = vision.FaceLandmarker.create_from_options(options_viso)

# --- 3. CONFIGURAZIONE WEBCAM E VARIABILI TEMPO ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Errore: webcam non trovata.")
    exit()

print("Sistema avviato. Premi 'q' per uscire.")
running = True

# Variabili per il cronometro speciale
tempo_mani_sopra_mento = 0.0
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

    # Specchia e converti l'immagine
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    h_frame, w_frame, _ = frame.shape

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame_rgb
    )

    timestamp_ms = int(time.time() * 1000)
    risultati_mani = detector_mani.detect_for_video(mp_image, timestamp_ms)
    risultati_viso = detector_viso.detect_for_video(mp_image, timestamp_ms)

    # Variabili di supporto per il frame corrente
    y_mento = None
    pt_mano_piu_alta = None
    min_y_mano = float('inf') # Inizializziamo a infinito per cercare il valore minimo

    # --- 5. ELABORAZIONE VISO & IDENTIFICAZIONE MENTO ---
    if risultati_viso.face_landmarks:
        face_landmarks = risultati_viso.face_landmarks[0]
        
        # Il punto 152 è la base inferiore del mento
        lm_mento = face_landmarks[152]
        y_mento = int(lm_mento.y * h_frame)
        x_mento = int(lm_mento.x * w_frame)
        
        # Disegno di tutti i punti del viso (Blu)
        for lm in face_landmarks:
            cx = int(lm.x * w_frame)
            cy = int(lm.y * h_frame)
            cv2.circle(frame, (cx, cy), 1, (255, 0, 0), -1)
            
        # Evidenzia il punto esatto del mento (Giallo)
        cv2.circle(frame, (x_mento, y_mento), 5, (0, 255, 255), -1)

    # --- 6. ELABORAZIONE MANI & RICERCA PUNTO PIÙ ALTO ---
    if risultati_mani.hand_landmarks:
        for hand_landmarks in risultati_mani.hand_landmarks:
            for lm in hand_landmarks:
                cx = int(lm.x * w_frame)
                cy = int(lm.y * h_frame)
                
                # Disegno di tutti i punti delle mani (Verde)
                cv2.circle(frame, (cx, cy), 2, (0, 255, 0), -1)
                
                # In OpenCV l'asse Y parte da 0 in alto e cresce verso il basso.
                # Quindi il punto "più alto" sullo schermo ha la coordinata Y più piccola.
                if cy < min_y_mano:
                    min_y_mano = cy
                    pt_mano_piu_alta = (cx, cy)

    # --- 7. LOGICA DEL CONFRONTO E CRONOMETRO ---
    condizione_soddisfatta = False

    if y_mento is not None and pt_mano_piu_alta is not None:
        # Disegna la linea immaginaria del mento (Bianca)
        cv2.line(frame, (0, y_mento), (w_frame, y_mento), (255, 255, 255), 1)
        
        # Evidenzia con un cerchio Rosso il punto più alto della mano
        cv2.circle(frame, pt_mano_piu_alta, 6, (0, 0, 255), 2)

        # Se la Y della mano è MINORE della Y del mento, la mano è più in alto del mento
        if pt_mano_piu_alta[1] < y_mento:
            tempo_mani_sopra_mento += delta_time
            condizione_soddisfatta = True

    # --- 8. GRAFICA E TIMER A SCHERMO ---
    colore_interfaccia = (0, 255, 0) if condizione_soddisfatta else (0, 0, 255)
    stato_testo = "MANI ALTE (ZONA VISO)" if condizione_soddisfatta else "MANI BASSE"
    
    cv2.putText(frame, f"Tempo Area Viso: {tempo_mani_sopra_mento:.1f} s", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, colore_interfaccia, 2)
    cv2.putText(frame, f"Stato: {stato_testo}", (10, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, colore_interfaccia, 2)

    # Mostra la finestra sviluppata
    cv2.imshow("Tracciamento Altezza Mani vs Mento", frame)

    # Gestione uscita
    tasto = cv2.waitKey(1) & 0xFF
    if tasto == ord("q"):
        running = False

# --- 9. CHIUSURA E RESOCONTO FINALE SUL TERMINALE ---
cap.release()
cv2.destroyAllWindows()
detector_mani.close()
detector_viso.close()

print("\n" + "="*50)
print(f" TEMPO TOTALIZZATO CON LE MANI SOPRA IL MENTO: {tempo_mani_sopra_mento:.2f} secondi")
print("="*50 + "\n")