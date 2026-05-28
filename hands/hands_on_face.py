# Tracking secondi in cui le mani si sovrappongono al viso (potenziale segno di stress/insicurezza)
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
    print("Sto scaricando il file dell'IA per il viso...")
    url_viso = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(url_viso, modello_viso_path)

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

# Variabile per il cronometro della sovrapposizione
tempo_sovrapposizione = 0.0
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

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    timestamp_ms = int(time.time() * 1000)
    
    risultati_mani = detector_mani.detect_for_video(mp_image, timestamp_ms)
    risultati_viso = detector_viso.detect_for_video(mp_image, timestamp_ms)

    # Variabili di supporto per la sovrapposizione
    area_viso = None
    condizione_soddisfatta = False

    
 #--- 5. ELABORAZIONE VISO & CREAZIONE BOUNDING BOX ESPANSO ---
    if risultati_viso.face_landmarks:
        face_landmarks = risultati_viso.face_landmarks[0]
        
        # Estraiamo tutte le coordinate X e Y del viso per creare un perimetro base
        xs = [int(lm.x * w_frame) for lm in face_landmarks]
        ys = [int(lm.y * h_frame) for lm in face_landmarks]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # --- MODIFICA: ESPANSIONE PER LE ORECCHIE ---
        # Calcoliamo la larghezza del viso
        larghezza_viso = max_x - min_x
        
        # Aggiungiamo un margine dinamico (15% della larghezza) a destra e sinistra
        margine_orecchie = int(larghezza_viso * 0.15) 
        
        # Aggiorniamo i limiti X assicurandoci di non uscire fuori dallo schermo
        # max(0, ...) impedisce di andare sotto zero
        # min(w_frame, ...) impedisce di superare la larghezza massima del video
        min_x = max(0, min_x - margine_orecchie)
        max_x = min(w_frame, max_x + margine_orecchie)
        
        # Opzionale: puoi alzare leggermente anche min_y se vuoi includere meglio i capelli/fronte alta
        # margine_fronte = int((max_y - min_y) * 0.10)
        # min_y = max(0, min_y - margine_fronte)
        # -------------------------------------------
        
        area_viso = (min_x, min_y, max_x, max_y)
        
        # Disegna il rettangolo attorno al viso (Bianco, diventerà Rosso se toccato)
        cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (255, 255, 255), 1)





    # --- 6. ELABORAZIONE MANI & VERIFICA SOVRAPPOSIZIONE ---
    if risultati_mani.hand_landmarks and area_viso:
        min_x, min_y, max_x, max_y = area_viso
        
        for hand_landmarks in risultati_mani.hand_landmarks:
            for lm in hand_landmarks:
                cx = int(lm.x * w_frame)
                cy = int(lm.y * h_frame)
                
                # Controlla se il punto della mano è DENTRO l'area del viso
                if min_x <= cx <= max_x and min_y <= cy <= max_y:
                    condizione_soddisfatta = True
                    # Evidenzia il punto della mano che sta toccando il viso (Rosso)
                    cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
                else:
                    # Disegna normalmente i punti delle mani (Verde)
                    cv2.circle(frame, (cx, cy), 2, (0, 255, 0), -1)

    # --- 7. AGGIORNAMENTO CRONOMETRO ---
    if condizione_soddisfatta:
        tempo_sovrapposizione += delta_time

    # --- 8. GRAFICA E TIMER A SCHERMO ---
    colore_interfaccia = (0, 0, 255) if condizione_soddisfatta else (0, 255, 0)
    stato_testo = "CONTATTO VISO RILEVATO!" if condizione_soddisfatta else "Nessun contatto"
    
    # Se c'è contatto, coloro anche il rettangolo del viso di rosso per feedback visivo
    if condizione_soddisfatta and area_viso:
         cv2.rectangle(frame, (area_viso[0], area_viso[1]), (area_viso[2], area_viso[3]), (0, 0, 255), 2)
    
    cv2.putText(frame, f"Tempo Contatto: {tempo_sovrapposizione:.1f} s", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, colore_interfaccia, 2)
    cv2.putText(frame, f"Stato: {stato_testo}", (10, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, colore_interfaccia, 2)

    cv2.imshow("Analisi Contatto Mano-Viso", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        running = False

# --- 9. CHIUSURA E RESOCONTO FINALE ---
cap.release()
cv2.destroyAllWindows()
detector_mani.close()
detector_viso.close()

print("\n" + "="*50)
print(f" TEMPO TOTALE CONTATTO MANO-VISO: {tempo_sovrapposizione:.2f} secondi")
print("="*50 + "\n")