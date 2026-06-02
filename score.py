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
        "hand_gravity" : (5.0, 35.0, 55.0, 80.0),
        "head_total": (5.0, 25.0, 60.0, 85.0),
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
    


def valuta_metrica_speech(valore, parametro_base, nome_metrica):
    """
    Calcola il rate corretto (su 100 parole, al minuto o assoluto) 
    e restituisce il pallino colorato e le statistiche per lo speech.
    """
    # Soglie: (min_rosso, min_giallo, max_giallo, max_rosso)
    # Nota: per metriche in cui "0" è il valore perfetto, min_rosso e min_giallo sono settati a -1.0 per non essere mai attivati.
    soglie = {
        "vocal_fillers": (1.0, 2.0, 5.0, 8.0),     # Campana: <1 Rosso, 2-5 Verde, 6-8 Giallo, >8 Rosso
        "filler_words": (-1.0, -1.0, 2.0, 5.0),    # Lineare: 0-2 Verde, 3-5 Giallo, >5 Rosso
        "micro_silences": (-1.0, -1.0, 5.0, 12.0), # Lineare: 0-5 Verde, 6-12 Giallo, >12 Rosso
        "long_pauses": (-1.0, -1.0, 0.0, 1.0),     # Assoluto: 0 Verde, 1 Giallo, >=2 Rosso
        "tremor": (-1.0, -1.0, 33.0, 66.0)         # Assoluto: <33 Verde, 33-66 Giallo, >66 Rosso
    }
    
    # 1. Calcoliamo il "valore_calcolato" in base al tipo di metrica
    if nome_metrica in ["vocal_fillers", "filler_words"]:
        # Calcolo: rate ogni 100 parole
        base_parole = max(parametro_base, 1) # evita divisione per zero
        valore_calcolato = (valore / base_parole) * 100
        
    elif nome_metrica == "micro_silences":
        # Calcolo: rate al minuto
        base_secondi = max(parametro_base, 0.1)
        valore_calcolato = (valore / base_secondi) * 60
        
    else:
        # long_pauses e tremor sono valori assoluti, non vanno divisi
        valore_calcolato = valore
        
    # 2. Estraiamo i 4 limiti
    min_rosso, min_giallo, max_giallo, max_rosso = soglie.get(nome_metrica, (0, 0, 100, 100))
    pallino = "●"
    
    # 3. Assegnazione colore in base ai limiti
    if valore_calcolato < min_rosso:
        colore = "#F44336" # Rosso (Es. 0 vocal fillers -> troppo robotico)
    elif valore_calcolato >= min_rosso and valore_calcolato < min_giallo:
        colore = "#FF9800" # Giallo (Sotto la soglia verde)
    elif valore_calcolato >= min_giallo and valore_calcolato <= max_giallo:
        colore = "#4CAF50" # Verde (Fascia ideale)
    elif valore_calcolato > max_giallo and valore_calcolato <= max_rosso:
        colore = "#FF9800" # Giallo (Sopra la soglia verde)
    else: 
        colore = "#F44336" # Rosso (Grave)
        
    return {
        "valore_reale": valore,
        "valore_calcolato": round(valore_calcolato, 1),
        "pallino": pallino,
        "colore": colore
    }

def valuta_performance_speech(speech_data_dict):
    """
    Raccoglie tutti i dati speech di una domanda, conta le parole totali
    e impacchetta ogni statistica con il suo colore.
    """
    durata_sec = speech_data_dict.get("audio_duration", 1.0)
    testo_risposta = speech_data_dict.get("text", "")
    
    # Calcoliamo quante parole ha detto l'utente nella risposta
    # (Se la trascrizione è vuota, consideriamo 1 parola per evitare errori matematici)
    total_words = max(len(testo_risposta.split()), 1)
    
    report_valutato = {}
    
    # 1. Vocal Fillers (Calcolati sulle parole totali)
    report_valutato["vocal_fillers"] = valuta_metrica_speech(
        speech_data_dict.get('vocal_fillers', 0), 
        total_words, 
        "vocal_fillers"
    )
    
    # 2. Filler Words (Calcolate sulle parole totali)
    report_valutato["filler_words"] = valuta_metrica_speech(
        speech_data_dict.get('filler_words', 0), 
        total_words, 
        "filler_words"
    )
    
    # 3. Micro Silenzi (Calcolati sulla durata in secondi)
    report_valutato["micro_silences"] = valuta_metrica_speech(
        speech_data_dict.get('micro_silences', 0), 
        durata_sec, 
        "micro_silences"
    )
    
    # 4. Silenzi Lunghi / Panico (Valore assoluto, la base non serve)
    report_valutato["long_pauses"] = valuta_metrica_speech(
        speech_data_dict.get('silence_count', 0), 
        None, 
        "long_pauses"
    )
    
    # 5. Jitter / Tremore (Già scalato da 0 a 100, la base non serve)
    report_valutato["tremor"] = valuta_metrica_speech(
        speech_data_dict.get('tremor', 0), 
        None, 
        "tremor"
    )
    
    return report_valutato