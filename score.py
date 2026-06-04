# score.py

def cv_metric_evaluation(sec_value, total_time, metric_name):
    # Thresholds: (min_red, min_yellow, max_yellow, max_red)
    thresholds = {
        "eye_gaze_time": (10.0, 30.0, 60.0, 85.0),
        "face_tremor_time": (15.0, 35.0, 65.0, 85.0),
        "head_movement_time": (20.0, 40.0, 65.0, 85.0),
        "head_down": (20.0, 40.0, 65.0, 85.0),
        "hand_general_time": (20.0, 40.0, 65.0, 85.0),
        "face_touch_time": (10.0, 20.0, 40.0, 60.0), 
        "hand_gravity" : (5.0, 35.0, 55.0, 80.0),
        "head_total": (5.0, 25.0, 60.0, 85.0),
        "face_overlap_time": (5.0, 10.0, 20.0, 40.0)  
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
    
    # --- head total e hand gravity ---
    head_down_time = face_data.get('head_down', 0.0)
    head_moved_time = face_data.get('head_movement_time', 0.0)
    eye_gaze_time = face_data.get('eye_gaze_time', 0.0)
    face_tremor_time = face_data.get('face_tremor_time', 0.0)
    head_total_raw = (1.2* (head_down_time) + 0.4 * head_moved_time + 1.2 * eye_gaze_time + 0.2 * face_tremor_time) / total_time * 100
    
    hand_general_time = hand_data.get('hand_general_time', 0.0)
    hands_above_chin_time = hand_data.get('hands_above_chin_time', 0.0)
    box_overlap_time = hand_data.get('face_overlap_time', 0.0)
    hand_gravity_raw = (0.6 * (hand_general_time - hands_above_chin_time) + 0.8 * (hands_above_chin_time - box_overlap_time) + 1.3* (box_overlap_time)) / total_time * 100
    # -------------------------------------------------

    evaluated_report = {}
    
    evaluated_report["head_total"] = min(head_total_raw, 100.0)
    evaluated_report["hand_gravity"] = min(hand_gravity_raw, 100.0)
    
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
        "vocal_fillers": (1.0, 2.0, 5.0, 8.0),     
        "filler_words": (-1.0, -1.0, 2.0, 5.0),    
        "micro_silences": (-1.0, -1.0, 5.0, 12.0), 
        "long_pauses": (-1.0, -1.0, 0.0, 1.0),     
        "tremor": (-1.0, -1.0, 33.0, 66.0)         
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