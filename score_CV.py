#notebook 

## DA GEMINI: CALCOLO DELLO SCORE DI HANDS DETECTION PER OGNI DOMANDA
#io ne ho un altro, da controllare quali equazioni funzionano meglio

# x= tempo di detection_hands.py
# y= tempo di hands_movements.py

"""
def calcola_punteggio_gesticolazione(tempo_x_visibili, tempo_y_alte, tempo_totale):
    
    #Calcola un punteggio unico da 0 a 100 sulla qualità della gesticolazione.
    
    if tempo_totale <= 0:
        return 0.0

    # Calcolo percentuali sul tempo totale
    perc_x = (tempo_x_visibili / tempo_totale) * 100
    perc_y = (tempo_y_alte / tempo_totale) * 100

    # --- 1. CALCOLO PUNTEGGIO BASE (Basato su X) ---
    punteggio = 0.0
    
    if 15 <= perc_x <= 55:
        # Range d'oro: punteggio pieno
        punteggio = 100.0
    elif perc_x < 15:
        # Troppo rigido: il punteggio sale proporzionalmente (0% -> 0 punti, 15% -> 100 punti)
        punteggio = (perc_x / 15.0) * 100.0
    elif perc_x > 55:
        # Troppo movimento: togliamo 1.5 punti per ogni punto percentuale oltre il 55%
        punteggio = 100.0 - ((perc_x - 55.0) * 1.5)
        
    punteggio = max(0.0, punteggio) # Assicuriamoci che non vada sotto zero

    # --- 2. APPLICAZIONE PENALITÀ (Basata su Y) ---
    # Scegliamo un moltiplicatore severo: ogni 1% di mani in faccia toglie 5 punti.
    moltiplicatore_penalita = 5.0
    penalita = perc_y * moltiplicatore_penalita
    
    punteggio_finale = punteggio - penalita

    # --- 3. NORMALIZZAZIONE ---
    # Limitiamo il risultato finale strettamente tra 0 e 100
    return max(0.0, min(100.0, punteggio_finale))

# --- Esempio di utilizzo nel tuo ciclo while ---
# score = calcola_punteggio_gesticolazione(tempo_mani, tempo_mani_alte, tempo_totale_video)
# cv2.putText(frame, f"Score Gesti: {int(score)}%", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

"""