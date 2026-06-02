# utils.py
import customtkinter as ctk
from config import APP_FONT

DEFAULT_INTERVIEW_DATA = [
    {
        "question": "Tell me about yourself.",
        "text": "well basically i am a student and uhm i like coding.",
        "audio_duration": 45.0,     
        "micro_silences": 2,        
        "silence_count": 2,
        "vocal_fillers": 1,
        "vocal_fillers_dict": {"uhm": 1},
        "filler_words": 2,
        "filler_words_dict": {"basically": 1, "well": 1},
        "tremor": 1.2,
        "cv_data": {
            "gaze_face": {
                "total_time_answer": 43.3,
                "eye_gaze_time": 4.1,
                "face_tremor_time": 3.2,
                "head_movement_time": 2.8,
                "head_down": 3.5,
                "head_total": 2.6
            },
            "hand_gesture": {
                "total_time_answer": 43.3,
                "hand_general_time": 2.1,
                "face_touch_time": 1.5,
                "face_overlap_time": 0.8,
                "hand_gravity": 5.4
            }
        }
    },
    {
        "question": "What is your greatest weakness?",
        "text": "i think like my greatest weakness is basically public speaking.",
        "audio_duration": 35.0,     
        "micro_silences": 1,        
        "silence_count": 1,
        "vocal_fillers": 0,
        "vocal_fillers_dict": {},
        "filler_words": 2,
        "filler_words_dict": {"like": 1, "basically": 1},
        "tremor": 2.5,
        "cv_data": {
            "gaze_face": {
                "total_time_answer": 43.3,
                "eye_gaze_time": 4.1,
                "face_tremor_time": 3.2,
                "head_movement_time": 2.8,
                "head_down": 3.5,
                "head_total": 2.6
            },
            "hand_gesture": {
                "total_time_answer": 43.3,
                "hand_general_time": 2.1,
                "face_touch_time": 1.5,
                "face_overlap_time": 0.8,
                "hand_gravity": 5.4
            }
        }
    }
]


def generate_report_text(data, final_score): #####da modificare?
    report_text = "========================================================\n"
    report_text += "                 INTERVIEW REPORT                        \n"
    report_text += "========================================================\n\n"
    
    report_text += "--- QUESTIONS & ANSWERS ANALYSIS ---\n\n"

    for idx, item in enumerate(data):
        report_text += f"Q{idx+1}: {item['question']}\n"
        report_text += f"Your answer: \"{item['text']}\"\n\n"
        
        v_count = item.get('vocal_fillers', 0)
        v_dict = item.get('vocal_fillers_dict', {})
        f_count = item.get('filler_words', 0)
        f_dict = item.get('filler_words_dict', {})
        
        report_text += "[Speech Analysis]\n"
        report_text += f"- Audio Duration: {item.get('audio_duration', 0.0):.1f}s\n"
        report_text += f"- Long Pauses: {item.get('silence_count', 0)}\n"
        report_text += f"- Micro Silences: {item.get('micro_silences', 0)}\n"
        
        report_text += f"- Vocal Fillers: {v_count}\n"
        if v_count > 0:
            for word, count in v_dict.items():
                report_text += f"    * {word} [{count}]\n"
                
        report_text += f"- Filler Words: {f_count}\n"
        if f_count > 0:
            for word, count in f_dict.items():
                report_text += f"    * {word} [{count}]\n"
                
        report_text += f"- Voice Tremor: {item.get('tremor', 0)} / 100\n\n"

        cv_data = item.get("cv_data", {})
        cv_face = cv_data.get("gaze_face", {})
        cv_hand = cv_data.get("hand_gesture", {})

        report_text += "[Gaze and Face Analysis]\n"
        report_text += f"- Total Gaze Gravity Score: {cv_face.get('head_total', 0.0):.1f}%\n"
        report_text += f"- Eyes Distracted Time: {cv_face.get('eye_gaze_time', 0.0):.1f}s\n"
        report_text += f"- Head Turn Time: {cv_face.get('head_movement_time', 0.0):.1f}s\n"
        report_text += f"- Head Down Time: {cv_face.get('head_down', 0.0):.1f}s\n"
        report_text += f"- Nodding / Face Tremor Time: {cv_face.get('face_tremor_time', 0.0):.1f}s\n\n"

        report_text += "[Hand and Gesture Analysis]\n"
        report_text += f"- Total Gesture Gravity Score: {cv_hand.get('hand_gravity', 0.0):.1f}%\n"
        report_text += f"- Gesticulation Time: {cv_hand.get('hand_general_time', 0.0):.1f}s\n"
        report_text += f"- Big Gestures Time: {cv_hand.get('face_touch_time', 0.0):.1f}s\n"
        report_text += f"- Touching Face Time: {cv_hand.get('face_overlap_time', 0.0):.1f}s\n"
        report_text += "-" * 50 + "\n\n"

    report_text += "========================================================\n"
    report_text += "                 OVERALL FEEDBACK                       \n"
    report_text += "========================================================\n\n"
    report_text += f"Final Score: {final_score} / 100\n\n"
    
    report_text += "Questions to Review:\n"
    report_text += get_questions_to_review(data) + "\n\n"

    
    report_text += "Suggestions:\n"
    
    suggestions_list = generate_suggestions(data)
    
    if suggestions_list:
        for text, color in suggestions_list:
            if color == "#4CAF50":  # green (Optimal)
                report_text += f"+ Positive: {text}\n"
            else:                   # red (Low/High)
                report_text += f"- To improve: {text}\n"
    else:
        report_text += "No specific suggestions at this time.\n"

    return report_text

def generate_suggestions(data):
    """
    Analyze all the data from all queries and generate dynamic suggestions.
    Suggestions appear ONLY if the metric has been RED or GREEN
    at least (n // 2) + 1 times. Yellow values are ignored.
    """
    from suggestions import SUGGESTIONS
    
    cv_thresholds = {
        "eye_gaze_time": (10.0, 30.0, 60.0, 85.0),
        "face_tremor_time": (15.0, 35.0, 65.0, 85.0),
        "head_movement_time": (20.0, 40.0, 65.0, 85.0),
        "head_down": (20.0, 40.0, 65.0, 85.0),
        "hand_general_time": (20.0, 40.0, 65.0, 85.0),
        "face_touch_time": (10.0, 20.0, 40.0, 60.0), 
        "face_overlap_time": (5.0, 10.0, 20.0, 40.0)
    }
    
    speech_thresholds = {
        "vocal_fillers": (1.0, 2.0, 5.0, 8.0),     
        "filler_words": (-1.0, -1.0, 2.0, 5.0),    
        "micro_silences": (-1.0, -1.0, 5.0, 12.0), 
        "long_pauses": (-1.0, -1.0, 0.0, 1.0),     
        "tremor": (-1.0, -1.0, 33.0, 66.0)         
    }
    
    metric_mapping = {
        "eye_gaze_time": "eye_gaze_time",
        "face_tremor_time": "face_tremor_time",
        "head_movement_time": "head_movement_time",
        "head_down": "head_down",
        "hand_general_time": "hand_general_time",
        "face_touch_time": "face_touch_time",
        "face_overlap_time": "face_overlap_time",
        "vocal_fillers": "vocal_fillers",
        "filler_words": "filler_words",
        "micro_silences": "micro_silences",
        "long_pauses": "long_pauses",
        "tremor": "tremor"
    }
    
    num_questions = len(data)
    if num_questions == 0:
        return []
        
    threshold = (num_questions // 2) + 1  
    
    counters = {metric: {"low": 0, "high": 0, "optimal": 0} for metric in metric_mapping.keys()}
    
    for item in data:
        # ===== DATI CV/VISION =====
        cv_data = item.get("cv_data", {})
        face_data = cv_data.get("gaze_face", {})
        hand_data = cv_data.get("hand_gesture", {})
        
        tot_time = max(face_data.get("total_time_answer", 1.0), 0.1)
        
        cv_metrics = {
            "eye_gaze_time": face_data.get('eye_gaze_time', 0.0),
            "face_tremor_time": face_data.get('face_tremor_time', 0.0),
            "head_movement_time": face_data.get('head_movement_time', 0.0),
            "head_down": face_data.get('head_down', 0.0),
            "hand_general_time": hand_data.get('hand_general_time', 0.0),
            "face_touch_time": hand_data.get('face_touch_time', 0.0),
            "face_overlap_time": hand_data.get('face_overlap_time', 0.0),
        }
        
        for metric_key, sec__value in cv_metrics.items():
            min_red, min_yellow, max_yellow, max_red = cv_thresholds.get(metric_key, (0, 0, 100, 100))
            percentage = (sec__value / tot_time) * 100
            
            # count only if it's Red (Low/High) or Green (Optimal). Ignore Yellow.
            if percentage < min_red:
                counters[metric_key]["low"] += 1
            elif percentage > max_red:
                counters[metric_key]["high"] += 1
            elif min_yellow <= percentage <= max_yellow:
                counters[metric_key]["optimal"] += 1
        
        # speech metrics
        testo_risposta = item.get("text", "")
        durata_audio = max(item.get("audio_duration", 0.1), 0.1)
        total_words = max(len(testo_risposta.split()), 1)
        
        vocal_fillers_rate = (item.get("vocal_fillers", 0) / total_words) * 100 
        filler_words_rate = (item.get("filler_words", 0) / total_words) * 100 
        micro_silences_rate = (item.get("micro_silences", 0) / durata_audio) * 60  
        
        speech_metrics = {
            "vocal_fillers": vocal_fillers_rate,
            "filler_words": filler_words_rate,
            "micro_silences": micro_silences_rate,
            "long_pauses": item.get("silence_count", 0),
            "tremor": item.get("tremor", 0)
        }
        
        for metric_key, valore in speech_metrics.items():
            min_red, min_yellow, max_yellow, max_red = speech_thresholds.get(metric_key, (-1.0, -1.0, 100, 100))
            
            # Count only if it's Red (Low/High) or Green (Optimal). Ignore Yellow.
            if valore < min_red:
                counters[metric_key]["low"] += 1
            elif valore > max_red:
                counters[metric_key]["high"] += 1
            elif min_yellow <= valore <= max_yellow:
                counters[metric_key]["optimal"] += 1
    
    suggestions_list = []
    
    for metric_key, counts in counters.items():
        suggestion_key = metric_mapping.get(metric_key)
        
        if suggestion_key not in SUGGESTIONS:
            continue
        
        # Suggestions are populated ONLY if they exceed the majority threshold
        if counts["optimal"] >= threshold and "optimal" in SUGGESTIONS[suggestion_key]:
            suggestions_list.append((SUGGESTIONS[suggestion_key]["optimal"], "#4CAF50"))  # green
        elif counts["low"] >= threshold and "low" in SUGGESTIONS[suggestion_key]:
            suggestions_list.append((SUGGESTIONS[suggestion_key]["low"], "#F44336"))  # red
        elif counts["high"] >= threshold and "high" in SUGGESTIONS[suggestion_key]:
            suggestions_list.append((SUGGESTIONS[suggestion_key]["high"], "#F44336"))  # red
            
    return suggestions_list

def add_dot(parent_frame, label_text, val_dict):
            regular_font = (APP_FONT, 14)
            row = ctk.CTkFrame(parent_frame, fg_color="transparent")
            row.pack(anchor="center", pady=4)
            
            dot_color = val_dict.get('color', '#333333')
            dot = val_dict.get('dot', '')
            
            ctk.CTkLabel(row, text=f"{dot} ", font=regular_font, text_color=dot_color).pack(side="left")
            
            ctk.CTkLabel(row, text=label_text, font=regular_font, text_color="#333333").pack(side="left")


def get_questions_to_review(data):
    """
    Analyze the total scores (Speech, Gaze, Hand) for each question.
    If at least 2 out of 3 categories are in the red (too high or too low),
    the question is flagged for review.
    """
    from score import speech_performance_evaluation
    
    questions_to_review = []
    
    for idx, item in enumerate(data):
        red_count = 0
        
        report_speech = speech_performance_evaluation(item)
        val_long = report_speech.get("long_pauses", {}).get('calculated_value', 0)
        val_micro = report_speech.get("micro_silences", {}).get('calculated_value', 0)
        val_vocal = report_speech.get("vocal_fillers", {}).get('calculated_value', 0)
        val_filler = report_speech.get("filler_words", {}).get('calculated_value', 0)
        val_tremor = report_speech.get("tremor", {}).get('calculated_value', 0)
        
        speech_gravity_raw = (
            val_tremor * 0.4 + 
            val_long * 20 + 
            val_micro * 1.5 + 
            max(0, val_filler - 2) * 5 + 
            abs(val_vocal - 3.5) * 5
        )
        speech_percent = int(max(0, min(100, speech_gravity_raw)))
        
        if speech_percent < 5.0 or speech_percent > 85.0:
            red_count += 1
            
        # --- gaze percent (head_total) ---
        cv_data = item.get("cv_data", {})
        cv_face = cv_data.get("gaze_face", {})
        gaze_percent = int(cv_face.get('head_total', 0.0))
        
        if gaze_percent < 5.0 or gaze_percent > 85.0:
            red_count += 1
            
        # --- hand percent (hand_gravity) ---
        cv_hand = cv_data.get("hand_gesture", {})
        hand_percent = int(cv_hand.get('hand_gravity', 0.0))
        
        if hand_percent < 5.0 or hand_percent > 80.0:
            red_count += 1
            
        # --- evaluation ---
        if red_count >= 2:
            questions_to_review.append(f"• Q{idx+1}: {item['question']}")
            
    if not questions_to_review:
        return "• No critical questions to review. Great job!"
        
    return "\n".join(questions_to_review)