# utils.py

# --- I tuoi dati fittizi di test (PARTE 1) ---
DEFAULT_INTERVIEW_DATA = [
    {
        "question": "Tell me about yourself.",
        "text": "well basically i am a student and uhm i like coding.",
        "silence_count": 2,
        "vocal_fillers": 1,
        "vocal_fillers_dict": {"uhm": 1},
        "filler_words": 2,
        "filler_words_dict": {"basically": 1, "well": 1},
        "tremor": 1.2,
        "cv_data": {
            "gaze_face": {
                "tempo_totale_risposta": 43.3,
                "eye_gaze_time": 4.1,
                "face_tremor_time": 3.2,
                "head_movement_time": 2.8,
                "head_down": 3.5,
                "head_total": 2.6
            },
            "hand_gesture": {
                "tempo_totale_risposta": 43.3,
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
        "silence_count": 1,
        "vocal_fillers": 0,
        "vocal_fillers_dict": {},
        "filler_words": 2,
        "filler_words_dict": {"like": 1, "basically": 1},
        "tremor": 2.5,
        "cv_data": {
            "gaze_face": {
                "tempo_totale_risposta": 43.3,
                "eye_gaze_time": 4.1,
                "face_tremor_time": 3.2,
                "head_movement_time": 2.8,
                "head_down": 3.5,
                "head_total": 2.6
            },
            "hand_gesture": {
                "tempo_totale_risposta": 43.3,
                "hand_general_time": 2.1,
                "face_touch_time": 1.5,
                "face_overlap_time": 0.8,
                "hand_gravity": 5.4
            }
        }
    }
]

# --- Funzione per generare il testo del report completo (PARTE 2) ---
def generate_report_text(data, final_score):
    testo_report = "========================================================\n"
    testo_report += "                 INTERVIEW REPORT                        \n"
    testo_report += "========================================================\n\n"
    
    testo_report += "--- QUESTIONS & ANSWERS ANALYSIS ---\n\n"

    for idx, item in enumerate(data):
        testo_report += f"Q{idx+1}: {item['question']}\n"
        testo_report += f"Your answer: \"{item['text']}\"\n\n"
        
        v_count = item.get('vocal_fillers', 0)
        v_dict = item.get('vocal_fillers_dict', {})
        f_count = item.get('filler_words', 0)
        f_dict = item.get('filler_words_dict', {})
        
        testo_report += "[Speech Analysis]\n"
        testo_report += f"- Long Pauses: {item.get('silence_count', 0)}\n"
        
        testo_report += f"- Vocal Fillers: {v_count}\n"
        if v_count > 0:
            for word, count in v_dict.items():
                testo_report += f"    * {word} [{count}]\n"
                
        testo_report += f"- Filler Words: {f_count}\n"
        if f_count > 0:
            for word, count in f_dict.items():
                testo_report += f"    * {word} [{count}]\n"
                
        testo_report += f"- Voice Tremor: {item.get('tremor', 0)} / 100\n\n"

        cv_data = item.get("cv_data", {})
        cv_face = cv_data.get("gaze_face", {})
        cv_hand = cv_data.get("hand_gesture", {})

        testo_report += "[Gaze and Face Analysis]\n"
        testo_report += f"- Score Total Face Movements: {cv_face.get('head_total', 0.0):.1f}s\n"
        testo_report += f"- Eyes Distracted Time: {cv_face.get('eye_gaze_time', 0.0):.1f}s\n"
        testo_report += f"- Face Tremor Time: {cv_face.get('face_tremor_time', 0.0):.1f}s\n"
        testo_report += f"- Head Moved/Turned Time: {cv_face.get('head_movement_time', 0.0):.1f}s\n\n"

        testo_report += "[Hand and Gesture Analysis]\n"
        testo_report += f"- Score Total Hand Gesture: {cv_hand.get('hand_gravity', 0.0):.1f}s\n"
        testo_report += f"- Gesticulation Time: {cv_hand.get('hand_general_time', 0.0):.1f}s\n"
        testo_report += f"- Hands Above Chin Time: {cv_hand.get('face_touch_time', 0.0):.1f}s\n"
        testo_report += f"- Touching Face Time: {cv_hand.get('face_overlap_time', 0.0):.1f}s\n"
        testo_report += "-" * 50 + "\n\n"

    testo_report += "========================================================\n"
    testo_report += "                 OVERALL FEEDBACK                       \n"
    testo_report += "========================================================\n\n"
    testo_report += f"Final Score: {final_score} / 100\n\n"
    
    testo_report += "Questions to Review:\n"
    testo_report += "* Q2: What is your greatest weakness? (High voice tremor detected)\n"
    testo_report += "* Q4: Where do you see yourself in 5 years? (Too many filler words)\n\n"
    
    testo_report += "Suggestions:\n"
    testo_report += "+ Positive: Your gaze was very steady and you maintained good eye contact.\n"
    testo_report += "+ Positive: You didn't touch your face and used hand gestures effectively to explain yourself.\n"
    testo_report += "- Negative: Your voice trembled significantly during some answers, try taking deep breaths.\n"
    testo_report += "- Negative: Try to reduce filler words like 'basically' and 'like'.\n"

    return testo_report