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
    testo_report += get_questions_to_review(data) + "\n\n"

    
    testo_report += "Suggestions:\n"
    
    # Richiamiamo le suggestions dinamiche
    suggestions_list = generate_suggestions(data)
    
    if suggestions_list:
        for text, color in suggestions_list:
            # Usiamo il codice colore per capire se è un feedback positivo o negativo nel file di testo
            if color == "#4CAF50":  # Verde (Optimal)
                testo_report += f"+ Positive: {text}\n"
            else:                   # Rosso (Low/High)
                testo_report += f"- To improve: {text}\n"
    else:
        testo_report += "No specific suggestions at this time.\n"

    return testo_report

def generate_suggestions(data):
    """
    Analizza tutti i dati di tutte le domande e genera suggestions dinamiche.
    Le suggestions compaiono SOLO se la metrica è risultata in ROSSO o in VERDE
    per almeno (n // 2) + 1 volte. I valori in giallo vengono ignorati.
    """
    from suggestions import SUGGESTIONS
    
    # 1. Soglie ALLINEATE ESATTAMENTE a quelle di score.py
    soglie_cv = {
        "eye_gaze_time": (10.0, 30.0, 60.0, 85.0),
        "face_tremor_time": (15.0, 35.0, 65.0, 85.0),
        "head_movement_time": (20.0, 40.0, 65.0, 85.0),
        "head_down": (20.0, 40.0, 65.0, 85.0),
        "hand_general_time": (20.0, 40.0, 65.0, 85.0),
        "face_touch_time": (10.0, 20.0, 40.0, 60.0), 
        "face_overlap_time": (5.0, 10.0, 20.0, 40.0)
    }
    
    soglie_speech = {
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
        
    # La soglia della maggioranza assoluta (es: 2 su 2, 2 su 3, 3 su 4...)
    threshold = (num_questions // 2) + 1  
    
    # Inizializziamo i contatori
    counters = {metric: {"low": 0, "high": 0, "optimal": 0} for metric in metric_mapping.keys()}
    
    # Analizza ogni domanda
    for item in data:
        # ===== DATI CV/VISION =====
        cv_data = item.get("cv_data", {})
        face_data = cv_data.get("gaze_face", {})
        hand_data = cv_data.get("hand_gesture", {})
        
        tempo_tot = max(face_data.get("tempo_totale_risposta", 1.0), 0.1)
        
        cv_metrics = {
            "eye_gaze_time": face_data.get('eye_gaze_time', 0.0),
            "face_tremor_time": face_data.get('face_tremor_time', 0.0),
            "head_movement_time": face_data.get('head_movement_time', 0.0),
            "head_down": face_data.get('head_down', 0.0),
            "hand_general_time": hand_data.get('hand_general_time', 0.0),
            "face_touch_time": hand_data.get('face_touch_time', 0.0),
            "face_overlap_time": hand_data.get('face_overlap_time', 0.0),
        }
        
        for metric_key, valore_sec in cv_metrics.items():
            min_rosso, min_giallo, max_giallo, max_rosso = soglie_cv.get(metric_key, (0, 0, 100, 100))
            percentuale = (valore_sec / tempo_tot) * 100
            
            # Conta SOLO se è Rosso (Estremi) o Verde (Ottimale). Ignora il Giallo.
            if percentuale < min_rosso:
                counters[metric_key]["low"] += 1
            elif percentuale > max_rosso:
                counters[metric_key]["high"] += 1
            elif min_giallo <= percentuale <= max_giallo:
                counters[metric_key]["optimal"] += 1
        
        # ===== DATI SPEECH =====
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
            min_rosso, min_giallo, max_giallo, max_rosso = soglie_speech.get(metric_key, (-1.0, -1.0, 100, 100))
            
            # Conta SOLO se è Rosso (Estremi) o Verde (Ottimale). Ignora il Giallo.
            if valore < min_rosso:
                counters[metric_key]["low"] += 1
            elif valore > max_rosso:
                counters[metric_key]["high"] += 1
            elif min_giallo <= valore <= max_giallo:
                counters[metric_key]["optimal"] += 1
    
    # Genera suggestions basate sui contatori definitivi
    suggestions_list = []
    
    for metric_key, counts in counters.items():
        suggestion_key = metric_mapping.get(metric_key)
        
        if suggestion_key not in SUGGESTIONS:
            continue
        
        # Le suggestions vengono popolate SOLO se superano il threshold della maggioranza
        if counts["optimal"] >= threshold and "optimal" in SUGGESTIONS[suggestion_key]:
            suggestions_list.append((SUGGESTIONS[suggestion_key]["optimal"], "#4CAF50"))  # Verde
        elif counts["low"] >= threshold and "low" in SUGGESTIONS[suggestion_key]:
            suggestions_list.append((SUGGESTIONS[suggestion_key]["low"], "#F44336"))  # Rosso
        elif counts["high"] >= threshold and "high" in SUGGESTIONS[suggestion_key]:
            suggestions_list.append((SUGGESTIONS[suggestion_key]["high"], "#F44336"))  # Rosso
            
    return suggestions_list

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


def get_questions_to_review(data):
    """
    Analizza i punteggi totali (Speech, Gaze, Hand) per ogni domanda.
    Se almeno 2 categorie su 3 sono in rosso (troppo o troppo poco),
    la domanda viene segnalata per la revisione.
    """
    from score import valuta_performance_speech
    
    questions_to_review = []
    
    for idx, item in enumerate(data):
        red_count = 0
        
        # --- 1. SPEECH PERCENT ---
        # Richiamiamo i dati per calcolare la percentuale esatta come in screen5
        report_speech = valuta_performance_speech(item)
        val_long = report_speech.get("long_pauses", {}).get('valore_calcolato', 0)
        val_micro = report_speech.get("micro_silences", {}).get('valore_calcolato', 0)
        val_vocal = report_speech.get("vocal_fillers", {}).get('valore_calcolato', 0)
        val_filler = report_speech.get("filler_words", {}).get('valore_calcolato', 0)
        val_tremor = report_speech.get("tremor", {}).get('valore_calcolato', 0)
        
        speech_gravity_raw = (
            val_tremor * 0.4 + 
            val_long * 20 + 
            val_micro * 1.5 + 
            max(0, val_filler - 2) * 5 + 
            abs(val_vocal - 3.5) * 5
        )
        speech_percent = int(max(0, min(100, speech_gravity_raw)))
        
        # Soglie da screen5: (5.0, 30.0, 60.0, 85.0)
        if speech_percent < 5.0 or speech_percent > 85.0:
            red_count += 1
            
        # --- 2. GAZE PERCENT (head_total) ---
        cv_data = item.get("cv_data", {})
        cv_face = cv_data.get("gaze_face", {})
        gaze_percent = int(cv_face.get('head_total', 0.0))
        
        # Soglie da screen5: (5.0, 25.0, 60.0, 85.0)
        if gaze_percent < 5.0 or gaze_percent > 85.0:
            red_count += 1
            
        # --- 3. HAND PERCENT (hand_gravity) ---
        cv_hand = cv_data.get("hand_gesture", {})
        hand_percent = int(cv_hand.get('hand_gravity', 0.0))
        
        # Soglie da screen5: (5.0, 35.0, 55.0, 80.0)
        if hand_percent < 5.0 or hand_percent > 80.0:
            red_count += 1
            
        # --- VALUTAZIONE ---
        if red_count >= 2:
            questions_to_review.append(f"• Q{idx+1}: {item['question']}")
            
    if not questions_to_review:
        return "• No critical questions to review. Great job!"
        
    return "\n".join(questions_to_review)