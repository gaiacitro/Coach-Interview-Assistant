# score.py
# Thresholds for colored bars and Final Score
BAR_THRESHOLDS = {
    "speech_gravity": (0.0, 5.0, 45.0, 75.0),
    "head_total": (0.0, 5.0, 24.0, 33.0),
    "hand_gravity": (0.0, 5.0, 20.0, 40.0)
}

CV_DOT_THRESHOLD = {
    "eye_gaze_time": (0.0, 2.0, 13.0, 16.0), ## looking_away
    "face_tremor_time": (0.0, 0.0, 10.0, 18.0), ## nodding
    "head_movement_time": (0.0, 1.5, 9.0, 16.0), ## 
    "head_down": (0.0, 0.0, 1.8, 3.5), ## looking_down
    "hand_general_time": (0.0, 2.0, 15.0, 25.0),  ## gestures
    "big_gestures": (0.0, 0.0, 6.0, 12.0), ## big_gesture
    "touching_face": (0.0, 0.0, 3.0, 4.3)   ## touching_face
}

SPEECH_DOT_THRESHOLD = {
    "vocal_fillers": (0.0, 0.0, 5.0, 8.0),     
    "filler_words": (0.0, 0.0, 2.0, 5.0),    
    "micro_silences": (0.0, 0.0, 5.0, 12.0), 
    "long_pauses": (0.0, 0.0, 0.0, 1.0),     
    "tremor": (0.0, 0.0, 33.0, 66.0),
    "words_per_minute": (90.0, 110.0, 160.0, 180.0) # NUOVA SOGLIA (Verde tra 110 e 160)
}


def cv_metric_evaluation(sec_value, total_time, metric_name):
    
    # t_m normalization (seconds per minute)
    total_time = max(total_time, 0.1)
    t_m = total_time / 60.0
    val_pm = sec_value / t_m
    
    min_red, min_yellow, max_yellow, max_red = CV_DOT_THRESHOLD.get(metric_name, (0, 0, 100, 100))
    dot = "●"
    
    if val_pm < min_red:
        color = "#F44336" 
    elif val_pm >= min_red and val_pm < min_yellow:
        color = "#FF9800" 
    elif val_pm >= min_yellow and val_pm <= max_yellow:
        color = "#4CAF50" 
    elif val_pm > max_yellow and val_pm <= max_red:
        color = "#FF9800" 
    else: 
        color = "#F44336" 
        
    return {
        "real_value": round(sec_value, 1),
        "calculated_value": round(val_pm, 1),
        "dot": dot,
        "color": color   
    }

def cv_performance_evaluation(cv_data_dict):
    face_data = cv_data_dict.get("gaze_face", {})
    hand_data = cv_data_dict.get("hand_gesture", {})
    
    total_time = max(face_data.get("total_time_answer", 1.0), 0.1) 
    
    # Convertiamo il tempo totale in minuti
    t_m = total_time / 60.0
    
    # --- HEAD GRAVITY SCORE (Tasso per Minuto) ---
    head_down_time = face_data.get('head_down', 0.0)
    head_moved_time = face_data.get('head_movement_time', 0.0)
    eye_gaze_time = face_data.get('eye_gaze_time', 0.0)
    face_tremor_time = face_data.get('face_tremor_time', 0.0)
    
    # Calcoliamo i "secondi di errore" per ogni minuto di video
    head_down_pm = head_down_time / t_m
    head_moved_pm = head_moved_time / t_m
    eye_gaze_pm = eye_gaze_time / t_m
    face_tremor_pm = face_tremor_time / t_m
    
    # Applichiamo i pesi ai valori al minuto. 
    # Esempio: se tieni la testa bassa per 10 sec al minuto, pesa di più di muovere la testa per 10 sec.
    head_total_raw = (1.3 * head_down_pm) + (0.5 * head_moved_pm) + (0.3 * eye_gaze_pm) + (0.5 * face_tremor_pm)
    
    # --- HAND GRAVITY SCORE (Tasso per Minuto) ---
    hand_general_time = hand_data.get('hand_general_time', 0.0)
    hands_above_chin_time = hand_data.get('hands_above_chin_time', 0.0)
    touching_face_time = hand_data.get('touching_face', 0.0)
    
    # Isoliamo i tempi per non contare i secondi due volte (es: mani sul volto implica anche mani sopra il mento)
    solo_hand_general = max(0, hand_general_time - hands_above_chin_time)
    solo_hands_above_chin = max(0, hands_above_chin_time - touching_face_time)
    
    # Calcoliamo i "secondi di errore" per ogni minuto di video
    hand_general_pm = solo_hand_general / t_m
    big_gestures_pm = solo_hands_above_chin / t_m
    touching_face_pm = touching_face_time / t_m
    
    # Applichiamo i pesi crescenti in base alla gravità del gesto
    hand_gravity_raw = (0.6 * hand_general_pm) + (0.4 * big_gestures_pm) + (1.3 * touching_face_pm) 
    # -------------------------------------------------

    evaluated_report = {}
    
    # Limitiamo il punteggio finale di gravità a 100.0 come massimale
    evaluated_report["head_total"] = min(head_total_raw, 100.0)
    evaluated_report["hand_gravity"] = min(hand_gravity_raw, 100.0)
    
    # 2. Manteniamo invariata la valutazione dei singoli "pallini" (che usano le percentuali e le soglie assolute per i feedback a schermo)
    evaluated_report["eye_gaze"] = cv_metric_evaluation(face_data.get('eye_gaze_time', 0.0), total_time, "eye_gaze_time")
    evaluated_report["head_movement"] = cv_metric_evaluation(face_data.get('head_movement_time', 0.0), total_time, "head_movement_time")
    evaluated_report["head_down"] = cv_metric_evaluation(face_data.get('head_down', 0.0), total_time, "head_down")
    evaluated_report["face_tremor"] = cv_metric_evaluation(face_data.get('face_tremor_time', 0.0), total_time, "face_tremor_time")

    evaluated_report["hand_general"] = cv_metric_evaluation(hand_data.get('hand_general_time', 0.0), total_time, "hand_general_time")
    evaluated_report["face_touch"] = cv_metric_evaluation(hand_data.get('big_gestures', 0.0), total_time, "big_gestures")
    evaluated_report["face_overlap"] = cv_metric_evaluation(hand_data.get('touching_face', 0.0), total_time, "touching_face")
    
    return evaluated_report
 

def speech_metric_evaluation(value, base_parameter, metric_name):
    
    if metric_name in ["vocal_fillers", "filler_words"]:
        word_base = max(base_parameter, 1) 
        calculated_value = (value / word_base) * 100
    elif metric_name == "micro_silences":
        base_second = max(base_parameter, 0.1)
        calculated_value = (value / base_second) * 60
    else:
        calculated_value = value

    min_red, min_yellow, max_yellow, max_red = SPEECH_DOT_THRESHOLD.get(metric_name, (0, 0, 100, 100))
    dot = "●" 
    
    if calculated_value < min_red:
        color = "#F44336" 
    elif calculated_value >= min_red and calculated_value < min_yellow:
        color = "#FF9800" 
    elif calculated_value >= min_yellow and calculated_value <= max_yellow:
        color = "#4CAF50"  
    elif calculated_value > max_yellow and calculated_value <= max_red:
        color = "#FF9800"  
    else: 
        color = "#F44336" 
        
    return {
        "real_value": value,  
        "calculated_value": round(calculated_value, 1),
        "dot": dot,
        "color": color        
    }

def speech_performance_evaluation(speech_data_dict):
    # Protezione per evitare divisioni per zero
    sec_duration = max(speech_data_dict.get("audio_duration", 1.0), 0.1)
    answer_text = speech_data_dict.get("text", "")
    
    total_words = max(len(answer_text.split()), 1)
    
    evaluated_report = {}
    
    # Calculate individual metrics for the colored dots
    evaluated_report["vocal_fillers"] = speech_metric_evaluation(
        speech_data_dict.get('vocal_fillers', 0), total_words, "vocal_fillers"
    )
    evaluated_report["filler_words"] = speech_metric_evaluation(
        speech_data_dict.get('filler_words', 0), total_words, "filler_words"
    )
    evaluated_report["micro_silences"] = speech_metric_evaluation(
        speech_data_dict.get('micro_silences', 0), sec_duration, "micro_silences"
    )
    evaluated_report["long_pauses"] = speech_metric_evaluation(
        speech_data_dict.get('silence_count', 0), None, "long_pauses"
    )
    evaluated_report["tremor"] = speech_metric_evaluation(
        speech_data_dict.get('tremor', 0), None, "tremor"
    )
    
    # compute words per minute (WPM) 
    t_m = sec_duration / 60.0
    wpm = total_words / t_m
    evaluated_report["words_per_minute"] = speech_metric_evaluation(
        wpm, None, "words_per_minute"
    )
    
    # compute the final speech gravity score based on weighted metrics
    val_long = evaluated_report["long_pauses"]["real_value"]
    val_micro = evaluated_report["micro_silences"]["real_value"]
    val_tremor = evaluated_report["tremor"]["calculated_value"]
    
    vocal_pct = evaluated_report["vocal_fillers"]["calculated_value"]
    filler_pct = evaluated_report["filler_words"]["calculated_value"]
    
    long_pm = val_long / t_m if t_m > 0 else 0
    micro_pm = val_micro / t_m if t_m > 0 else 0
    
    # let's add a penalty for speaking too slowly (below 100 WPM)
    wpm_penalty = 0
    if wpm < 100:
        wpm_penalty = (100 - wpm) * 0.5
        
    speech_gravity_raw = (
        (val_tremor * 0.4) +               
        (long_pm * 25) +                  
        (micro_pm * 1.5) +                
        (max(0, filler_pct - 2) * 2) +     
        (max(0, vocal_pct - 3) * 2) +
        wpm_penalty
    )
    
    # Let's save the score in the dictionary, limiting it to 100%
    evaluated_report["speech_gravity"] = min(speech_gravity_raw, 100.0)
    
    return evaluated_report

def calculate_perfection_score(gravity_value, thresholds):
    """
    Converts a severity score (bell curve) into a linear perfection score (0-100).
    Optimal performance is in the middle (between min_y and max_y).
    Too little movement (statue) or too much movement (anxious) reduces the score.
    """
    min_r, min_y, max_y, max_r = thresholds

    # 1. GREEN ZONE (Optimal amount of movement) -> Score 66 to 100
    if min_y <= gravity_value <= max_y:
        # Maximum perfection (100) is in the exact center of the green zone
        center = (min_y + max_y) / 2.0
        if gravity_value == center:
            return 100.0
        elif gravity_value < center:
            interval = center - min_y
            if interval > 0:
                return 66.0 + ((gravity_value - min_y) / interval) * 34.0
        else:
            interval = max_y - center
            if interval > 0:
                return 100.0 - ((gravity_value - center) / interval) * 34.0
        return 100.0

    # 2. LOWER YELLOW ZONE (Too little movement, slightly rigid) -> Score 33 to 66
    elif min_r <= gravity_value < min_y:
        interval = min_y - min_r
        if interval > 0:
            return 33.0 + ((gravity_value - min_r) / interval) * 33.0
        return 66.0

    # 3. LOWER RED ZONE (Completely frozen/statue) -> Score 0 to 33
    elif gravity_value < min_r:
        interval = min_r - 0.0
        if interval > 0:
            return ((gravity_value - 0.0) / interval) * 33.0
        return 33.0

    # 4. UPPER YELLOW ZONE (Too much movement, slightly anxious) -> Score 33 to 66
    elif max_y < gravity_value <= max_r:
        interval = max_r - max_y
        if interval > 0:
            return 66.0 - ((gravity_value - max_y) / interval) * 33.0
        return 66.0

    # 5. UPPER RED ZONE (Excessive movement, very anxious) -> Score 0 to 33
    else: # gravity_value > max_r
        if gravity_value >= 100.0:
            return 0.0
        interval = 100.0 - max_r
        if interval > 0:
            return 33.0 - ((gravity_value - max_r) / interval) * 33.0
        return 0.0