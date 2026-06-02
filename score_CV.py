# score_CV.py

def valuta_metrica(valore_sec, tempo_tot, nome_metrica):
    """
    Calcola la percentuale e restituisce il pallino colorato e il colore del testo.
    """
    # Soglie: (min_rosso, min_giallo, max_giallo, max_rosso)
    soglie = {
        "eye_gaze_time": (30.0, 50.0, 70.0, 85.0),
        "face_tremor_time": (15.0, 35.0, 65.0, 85.0),
        "head_movement_time": (20.0, 40.0, 65.0, 85.0),
        "head_down": (20.0, 40.0, 65.0, 85.0),
        "hand_general_time": (20.0, 40.0, 65.0, 85.0),
        "face_touch_time": (10.0, 20.0, 40.0, 60.0), 
        "face_overlap_time": (5.0, 10.0, 20.0, 40.0) 
    }
    
    # Sicurezza contro la divisione per zero
    tempo_tot = max(tempo_tot, 0.1)
    percentuale = (valore_sec / tempo_tot) * 100
    
    # Estraiamo i 4 limiti
    min_rosso, min_giallo, max_giallo, max_rosso = soglie.get(nome_metrica, (0, 0, 100, 100))
    pallino = "●"
    # Assegnazione pallino e colore
    if percentuale < min_rosso:
        colore = "#F44336" # Rosso
    elif percentuale >= min_rosso and percentuale < min_giallo:
        colore = "#FF9800" # Giallo/Arancione
    elif percentuale >= min_giallo and percentuale <= max_giallo:
        colore = "#4CAF50" # Verde
    elif percentuale > max_giallo and percentuale <= max_rosso:
        colore = "#FF9800" # Giallo/Arancione
    else: 
        colore = "#F44336" # Rosso
        
    return {
        "secondi": round(valore_sec, 1),
        "percentuale": round(percentuale, 1),
        "pallino": pallino,
        "colore": colore
    }

def valuta_performance_cv(cv_data_dict):
    """
    Raccoglie tutti i dati di una domanda, li valuta uno a uno e li impacchetta per l'interfaccia.
    """
    face_data = cv_data_dict.get("gaze_face", {})
    hand_data = cv_data_dict.get("hand_gesture", {})
    
    tempo_tot = max(face_data.get("tempo_totale_risposta", 1.0), 0.1)
    
    report_valutato = {}
    
    # Valutiamo il Viso
    report_valutato["eye_gaze"] = valuta_metrica(face_data.get('eye_gaze_time', 0.0), tempo_tot, "eye_gaze_time")
    report_valutato["head_movement"] = valuta_metrica(face_data.get('head_movement_time', 0.0), tempo_tot, "head_movement_time")
    report_valutato["head_down"] = valuta_metrica(face_data.get('head_down', 0.0), tempo_tot, "head_down")
    report_valutato["face_tremor"] = valuta_metrica(face_data.get('face_tremor_time', 0.0), tempo_tot, "face_tremor_time")

    # Valutiamo le Mani
    report_valutato["hand_general"] = valuta_metrica(hand_data.get('hand_general_time', 0.0), tempo_tot, "hand_general_time")
    report_valutato["face_touch"] = valuta_metrica(hand_data.get('face_touch_time', 0.0), tempo_tot, "face_touch_time")
    report_valutato["face_overlap"] = valuta_metrica(hand_data.get('face_overlap_time', 0.0), tempo_tot, "face_overlap_time")
    
    return report_valutato   
    #dizionario con chiavi: eye_gaze, head_movement, head_down, hand_general, face_touch, face_overlap dove
        # ognuna è un dizionario con chiavi: secondi, percentuale, pallino, colore
    