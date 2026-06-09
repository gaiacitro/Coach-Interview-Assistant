# score.py

def cv_metric_evaluation(sec_value, total_time, metric_name):
    # Thresholds: (min_red, min_yellow, max_yellow, max_red)
    thresholds = {
        "eye_gaze_time": (0.0, 2.0, 10.0, 17.0),
        "face_tremor_time": (0.0, 0.0, 3.5, 5.0),
        "head_movement_time": (0.0, 1.5, 7.0, 10.0),
        "head_down": (0.0, 0.0, 1.8, 3.0),
        "hand_general_time": (0.0, 2.0, 15.0, 20.0),   
        "face_touch_time": (0.0, 0.0, 2.0, 5.0), 
        "hand_gravity" : (5.0, 35.0, 55.0, 80.0),#QUESTO COME LO CAMBIO??
        "head_total": (5.0, 25.0, 60.0, 85.0),#QUESTO COME LO CAMBIO??
        "face_overlap_time": (0.0, 0.0, 5.0, 7.0)  
    }
    
    total_time = max(total_time, 0.1)
    percentage = (sec_value / total_time) * 100
    
    min_red, min_yellow, max_yellow, max_red = thresholds.get(metric_name, (0, 0, 100, 100))
    dot = "●"
    
    if percentage < min_red:
        color = "#F44336" 
    elif percentage >= min_red and percentage < min_yellow:
        color = "#FF9800" 
    elif percentage >= min_yellow and percentage <= max_yellow:
        color = "#4CAF50" 
    elif percentage > max_yellow and percentage <= max_red:
        color = "#FF9800" 
    else: 
        color = "#F44336" 
        
    return {
        "real_value": round(sec_value, 1),
        "calculated_value": round(percentage, 1),
        "dot": dot,
        "color": color   
    }

def cv_performance_evaluation(cv_data_dict):
    face_data = cv_data_dict.get("gaze_face", {})
    hand_data = cv_data_dict.get("hand_gesture", {})
    
    total_time = max(face_data.get("total_time_answer", 1.0), 0.1) 
    
    # 1. Convertiamo il tempo totale in minuti
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
    head_total_raw = (1.2 * head_down_pm) + (0.4 * head_moved_pm) + (1.2 * eye_gaze_pm) + (0.2 * face_tremor_pm)
    
    # --- HAND GRAVITY SCORE (Tasso per Minuto) ---
    hand_general_time = hand_data.get('hand_general_time', 0.0)
    hands_above_chin_time = hand_data.get('hands_above_chin_time', 0.0)
    box_overlap_time = hand_data.get('face_overlap_time', 0.0)
    
    # Isoliamo i tempi per non contare i secondi due volte (es: mani sul volto implica anche mani sopra il mento)
    solo_hand_general = max(0, hand_general_time - hands_above_chin_time)
    solo_hands_above_chin = max(0, hands_above_chin_time - box_overlap_time)
    
    # Calcoliamo i "secondi di errore" per ogni minuto di video
    hand_general_pm = solo_hand_general / t_m
    hands_above_chin_pm = solo_hands_above_chin / t_m
    box_overlap_pm = box_overlap_time / t_m
    
    # Applichiamo i pesi crescenti in base alla gravità del gesto
    hand_gravity_raw = (0.6 * hand_general_pm) + (0.8 * hands_above_chin_pm) + (1.3 * box_overlap_pm)
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
    evaluated_report["face_touch"] = cv_metric_evaluation(hand_data.get('face_touch_time', 0.0), total_time, "face_touch_time")
    evaluated_report["face_overlap"] = cv_metric_evaluation(hand_data.get('face_overlap_time', 0.0), total_time, "face_overlap_time")
    
    return evaluated_report
 

def speech_metric_evaluation(value, base_parameter, metric_name):
    thresholds = {
        "vocal_fillers": (0.0, 0.0, 5.0, 8.0),     
        "filler_words": (0.0, 0.0, 2.0, 5.0),    
        "micro_silences": (0.0, 0.0, 5.0, 12.0), 
        "long_pauses": (0.0, 0.0, 0.0, 1.0),     
        "tremor": (0.0, 0.0, 33.0, 66.0)         
    }
    
    if metric_name in ["vocal_fillers", "filler_words"]:
        word_base = max(base_parameter, 1) 
        calculated_value = (value / word_base) * 100
    elif metric_name == "micro_silences":
        base_second = max(base_parameter, 0.1)
        calculated_value = (value / base_second) * 60
    else:
        calculated_value = value

    min_red, min_yellow, max_yellow, max_red = thresholds.get(metric_name, (0, 0, 100, 100))
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
    
    # 1. Calcola le metriche individuali per i pallini colorati
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
    
    # 2. Calcola lo Speech Gravity Score totale (ora lo facciamo qui nel backend!)
    t_m = sec_duration / 60.0
    
    val_long = evaluated_report["long_pauses"]["real_value"]
    val_micro = evaluated_report["micro_silences"]["real_value"]
    val_vocal = evaluated_report["vocal_fillers"]["real_value"]
    val_filler = evaluated_report["filler_words"]["real_value"]
    val_tremor = evaluated_report["tremor"]["calculated_value"]
    
    long_pm = val_long / t_m if t_m > 0 else 0
    micro_pm = val_micro / t_m if t_m > 0 else 0
    filler_pm = val_filler / t_m if t_m > 0 else 0
    vocal_pm = val_vocal / t_m if t_m > 0 else 0
    
    speech_gravity_raw = (
        (val_tremor * 0.4) +               
        (long_pm * 25) +                  
        (micro_pm * 1.5) +                
        (max(0, filler_pm - 2) * 4) +     
        (max(0, vocal_pm - 3) * 4)       
    )
    
    # Salviamo il punteggio nel dizionario, limitandolo a 100%
    evaluated_report["speech_gravity"] = min(speech_gravity_raw, 100.0)
    
    return evaluated_report

def calculate_perfection_score(gravity_value, thresholds):
    """
    Converts a “bell-shaped” severity score into a linear score (0–100).
    New ranges: 0–33 (red), 33–66 (yellow), 66–100 (green).
    """
    min_r, min_y, max_y, max_r = thresholds

    # 1. Green range (66 - 100) -> Good/Excellent
    if min_y <= gravity_value <= max_y:
        # finding the midpoint between min_y and max_y to determine the perfect score point
        mid_green = (min_y + max_y) / 2.0
        if gravity_value <= mid_green:
            # gradually increases from 66 (yellow edge) to 100 (perfect center)
            return 66.0 + ((gravity_value - min_y) / (mid_green - min_y)) * 34.0 if mid_green > min_y else 100.0
        else:
            # gradually decreases from 100 (perfect center) to 66 (yellow edge)
            return 100.0 - ((gravity_value - mid_green) / (max_y - mid_green)) * 34.0 if max_y > mid_green else 100.0
            
    # 2. yellow range (33 - 66) -> decent
    if min_r <= gravity_value < min_y:
        # gradually increases from 33 (yellow edge) to 66 (green edge)
        return 33.0 + ((gravity_value - min_r) / (min_y - min_r)) * 33.0 if min_y > min_r else 33.0
        
    # 3. yellow range (66 - 33) -> decent
    if max_y < gravity_value <= max_r:
        # gradually decreases from 66 (green edge) to 33 (yellow edge)
        return 66.0 - ((gravity_value - max_y) / (max_r - max_y)) * 33.0 if max_r > max_y else 33.0
        
    # 4. lower red range (0 - 33) -> not sufficient
    if gravity_value < min_r:
        # gradually increases from 0 to 33
        return (gravity_value / min_r) * 33.0 if min_r > 0 else 0.0
        
    # 5. upper red range (33 - 0) -> not sufficient
    if gravity_value > max_r:
        if gravity_value >= 100.0:
            return 0.0
        # gradually decreases from 33 to 0
        return 33.0 - ((gravity_value - max_r) / (100.0 - max_r)) * 33.0
        
    return 0.0