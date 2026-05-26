# eye traking ma in realta è piu movimento di testa. se muovo solo gli occhi non lo prende. 


import cv2
import os
import urllib.request
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- FUNZIONE DI SMOOTHING ---
# Serve a rendere il movimento del "cursore oculare" fluido e non tremolante
def lerp(prev, new, alpha):
    return prev + alpha * (new - prev)

# --- 1. DOWNLOAD DEL MODELLO ---
modello_path = "face_landmarker.task"
if not os.path.exists(modello_path):
    print("Sto scaricando il file dell'IA per il viso...")
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(url, modello_path)

# --- 2. CONFIGURAZIONE MEDIAPIPE ---
base_options = python.BaseOptions(model_asset_path=modello_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    min_face_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.FaceLandmarker.create_from_options(options)

# --- 3. IMPOSTAZIONI FINESTRA E TESTO ---
LARGHEZZA_SCHERMO = 1000
ALTEZZA_SCHERMO = 600
cap = cv2.VideoCapture(0)

# Il testo inventato diviso in parole
frase = "Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura"
parole = frase.split()

# Calcoliamo dove posizionare le parole sullo schermo
parole_con_coordinate = []
x_corrente = 50
y_corrente = 300
spazio_tra_parole = 20

for parola in parole:
    # cv2.getTextSize ci restituisce la larghezza e altezza della singola parola
    (w, h), _ = cv2.getTextSize(parola, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 2)
    
    # Se la parola esce dallo schermo, andiamo a capo
    if x_corrente + w > LARGHEZZA_SCHERMO - 50:
        x_corrente = 50
        y_corrente += h + 40

    # Salviamo la parola e il suo "rettangolo di collisione" (Bounding Box)
    parole_con_coordinate.append({
        "testo": parola,
        "x": x_corrente,
        "y": y_corrente,
        "w": w,
        "h": h
    })
    x_corrente += w + spazio_tra_parole

# Variabili per il movimento fluido
cursore_x = LARGHEZZA_SCHERMO / 2
cursore_y = ALTEZZA_SCHERMO / 2
fluidita = 0.15 # Più è basso, più il cursore è "lento" e stabile
timestamp_ms = 0

print("Avvio in corso. Usa la testa/occhi per evidenziare le parole!")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    timestamp_ms += 33 
    
    risultati = detector.detect_for_video(mp_image, int(timestamp_ms))

    # Creiamo uno sfondo nero (o grigio scuro) per la nostra finestra di lettura
    schermo_lettura = np.full((ALTEZZA_SCHERMO, LARGHEZZA_SCHERMO, 3), 30, dtype=np.uint8)

    if risultati.face_landmarks:
        face_landmarks = risultati.face_landmarks[0]
        
        # Prendiamo il punto centrale tra i due occhi (punto 168, sopra il naso) 
        # o l'iride sx (468) come riferimento per muovere il nostro "cursore".
        # Usiamo il 468 (iride sinistra) come da tua richiesta originale.
        iride_sx = face_landmarks[468]
        
        # Mappiamo le coordinate normalizzate (0.0 - 1.0) sulle dimensioni della nostra finestra
        target_x = iride_sx.x * LARGHEZZA_SCHERMO
        target_y = iride_sx.y * ALTEZZA_SCHERMO
        
        # Applichiamo lo smoothing per evitare i tremolii della webcam
        cursore_x = lerp(cursore_x, target_x, fluidita)
        cursore_y = lerp(cursore_y, target_y, fluidita)

        # Disegniamo un piccolo puntino rosso per farti capire dove stai "mirando"
        cv2.circle(schermo_lettura, (int(cursore_x), int(cursore_y)), 5, (0, 0, 255), -1)

    # --- DISEGNO DELLE PAROLE E HIGHLIGHT ---
    for item in parole_con_coordinate:
        x, y, w, h = item["x"], item["y"], item["w"], item["h"]
        
        # Controlliamo se il cursore si trova dentro il rettangolo della parola.
        # (La Y del testo in OpenCV parte dal basso, quindi aggiustiamo la collisione)
        sta_guardando_la_parola = (x <= cursore_x <= x + w) and (y - h <= cursore_y <= y + 10)
        
        if sta_guardando_la_parola:
            # Sfondo evidenziatore giallo
            cv2.rectangle(schermo_lettura, (x - 5, y - h - 10), (x + w + 5, y + 10), (0, 255, 255), -1)
            # Testo nero
            colore_testo = (0, 0, 0)
            spessore = 3
        else:
            # Testo bianco normale
            colore_testo = (255, 255, 255)
            spessore = 2

        cv2.putText(schermo_lettura, item["testo"], (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, colore_testo, spessore)

    # Mostriamo la telecamera in piccolo (Picture in Picture) in alto a destra
    frame_piccolo = cv2.resize(frame, (200, 150))
    schermo_lettura[10:160, LARGHEZZA_SCHERMO-210:LARGHEZZA_SCHERMO-10] = frame_piccolo

    # Mostriamo la finestra finale
    cv2.imshow('Lettore Eye Tracking', schermo_lettura)

    if cv2.waitKey(5) & 0xFF == 27: # Tasto ESC per uscire
        break

cap.release()
cv2.destroyAllWindows()