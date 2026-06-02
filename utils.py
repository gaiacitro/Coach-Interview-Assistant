# utils.py
import customtkinter as ctk
from config import APP_FONT, TEXT_GREEN

# --- I tuoi dati fittizi di test (PARTE 1) ---
# utils.py
import customtkinter as ctk
from config import APP_FONT, TEXT_GREEN

# --- I tuoi dati fittizi di test (PARTE 1) ---
DEFAULT_INTERVIEW_DATA = [
    {
        "question": "Tell me about yourself.",
        "text": "well basically i am a student and uhm i like coding.",
        "audio_duration": 45.0,     # <--- AGGIUNTO
        "micro_silences": 2,        # <--- AGGIUNTO
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
        "audio_duration": 35.0,     # <--- AGGIUNTO
        "micro_silences": 1,        # <--- AGGIUNTO
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

# ... il resto del file rimane uguale ...

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
        # --- NUOVO: Aggiunti durata e micro silenzi ---
        testo_report += f"- Audio Duration: {item.get('audio_duration', 0.0):.1f}s\n"
        testo_report += f"- Long Pauses: {item.get('silence_count', 0)}\n"
        testo_report += f"- Micro Silences: {item.get('micro_silences', 0)}\n"
        
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
        # --- MODIFICATO: Punteggio totale in percentuale (%) e aggiunto Head Down ---
        testo_report += f"- Total Gaze Gravity Score: {cv_face.get('head_total', 0.0):.1f}%\n"
        testo_report += f"- Eyes Distracted Time: {cv_face.get('eye_gaze_time', 0.0):.1f}s\n"
        testo_report += f"- Head Turn Time: {cv_face.get('head_movement_time', 0.0):.1f}s\n"
        testo_report += f"- Head Down Time: {cv_face.get('head_down', 0.0):.1f}s\n"
        testo_report += f"- Nodding / Face Tremor Time: {cv_face.get('face_tremor_time', 0.0):.1f}s\n\n"

        testo_report += "[Hand and Gesture Analysis]\n"
        # --- MODIFICATO: Punteggio totale in percentuale (%) e aggiornati i nomi ---
        testo_report += f"- Total Gesture Gravity Score: {cv_hand.get('hand_gravity', 0.0):.1f}%\n"
        testo_report += f"- Gesticulation Time: {cv_hand.get('hand_general_time', 0.0):.1f}s\n"
        testo_report += f"- Big Gestures Time: {cv_hand.get('face_touch_time', 0.0):.1f}s\n"
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

def add_dot(parent_frame, label_text, val_dict):
            font_normale = (APP_FONT, 14)
            # Crea un contenitore invisibile orizzontale
            row = ctk.CTkFrame(parent_frame, fg_color="transparent")
            row.pack(anchor="center", pady=4)
            
            # Prepariamo i dati del pallino
            colore_pallino = val_dict.get('colore', '#333333')
            pallino = val_dict.get('pallino', '')
            
            # 1. Disegniamo PRIMA il pallino colorato (con uno spazietto a destra)
            ctk.CTkLabel(row, text=f"{pallino} ", font=font_normale, text_color=colore_pallino).pack(side="left")
            
            # 2. Disegniamo DOPO il testo, che si affiancherà alla destra del pallino
            ctk.CTkLabel(row, text=label_text, font=font_normale, text_color="#333333").pack(side="left")