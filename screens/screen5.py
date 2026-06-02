# screens/screen5.py
import customtkinter as ctk
from utils import (
    generate_report_text,
    DEFAULT_INTERVIEW_DATA,
    add_dot,
    generate_suggestions,
    get_questions_to_review
)  
from tkinter import filedialog
from score import valuta_performance_cv, valuta_performance_speech
from config import (
    CARD_BG, 
    CARD_BORDER, 
    TEXT_GREEN,
    TEXT_SUB,
    BTN_BG, 
    BTN_TEXT, 
    BTN_HOVER,
    APP_FONT
)
import threading
from ai_helper import get_reformulated_text # Importiamo la nostra IA!

def get_threshold_segments(canvas_w, canvas_h, soglie):
    """
    Genera i segmenti di una barra colorata basati su soglie percentuali.
    Ritorna una lista di (x_start, x_end, color)
    """
    min_rosso, min_giallo, max_giallo, max_rosso = soglie
    color_rosso = "#F44336"
    color_arancione = "#FF9800"
    color_verde = "#4CAF50"
    
    segments = []
    
    # Converti percentuali in pixel
    def pct_to_px(pct):
        return (pct / 100.0) * canvas_w
    
    threshold_points = [0, min_rosso, min_giallo, max_giallo, max_rosso, 100]
    threshold_colors = [color_rosso, color_arancione, color_verde, color_arancione, color_rosso]
    
    for i in range(len(threshold_points) - 1):
        x_start = pct_to_px(threshold_points[i])
        x_end = pct_to_px(threshold_points[i + 1])
        color = threshold_colors[i]
        
        if x_end > x_start:  # Solo se il segmento ha larghezza
            segments.append((x_start, x_end, color))
    
    return segments

class Screen5(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.pack(expand=True, fill="both") 
        
        # DEFINIZIONE DEI FONT
        font_titolo_grande = ctk.CTkFont(family=APP_FONT, size=34, weight="bold")
        font_titolo_sezione = ctk.CTkFont(family=APP_FONT, size=24, weight="bold")
        font_domanda = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")
        font_risposta = ctk.CTkFont(family=APP_FONT, size=15, slant="italic")
        font_titolo_box = ctk.CTkFont(family=APP_FONT, size=16, weight="bold")
        font_normale = ctk.CTkFont(family=APP_FONT, size=14)
        font_bottoni = ctk.CTkFont(family=APP_FONT, size=16, weight="bold")

        # CONTAINER INTERNO (Card principale)
        center_frame = ctk.CTkFrame(self, 
                                    fg_color=CARD_BG, 
                                    border_color=CARD_BORDER, 
                                    border_width=5, 
                                    corner_radius=20)
        center_frame.pack(pady=40, padx=40, ipadx=40, ipady=40, expand=True, fill="both")

        # TITLE SECTION 
        # Modifica 1: Aggiunto pady=40 anche sopra per non tagliare il bordo della card!
        ctk.CTkLabel(center_frame, text="Interview Report", font=font_titolo_grande, text_color=TEXT_GREEN).pack(anchor="center", pady=(40, 40))

        # Se non arrivano dati reali dall'intervista, carica il mock dal file utils
        if not data:
            data = DEFAULT_INTERVIEW_DATA

        # =========================================================
        # 1. FIRST PART: QUESTION BY QUESTION REPORT
        # =========================================================
        ctk.CTkLabel(center_frame, text="Questions & Answers Analysis", font=font_titolo_sezione, text_color=TEXT_SUB).pack(anchor="w", pady=(10, 20), padx=20)

        all_question_scores = []  # Lista per raccogliere i punteggi di ogni domanda

        for idx, item in enumerate(data):
            card = ctk.CTkFrame(center_frame, fg_color="white", corner_radius=15, border_width=2, border_color="#E8ECE8")
            card.pack(fill="x", pady=15, padx=20, ipady=15, ipadx=15)

            ctk.CTkLabel(card, text=f"Q{idx+1}: {item['question']}", font=font_domanda, text_color=TEXT_GREEN, wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(card, text=f"Your answer: \"{item['text']}\"", font=font_risposta, text_color="#555555", wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(0, 5))
            
            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            tempo_risposta = cv_face.get("tempo_totale_risposta", 0.0)
            
            # Ridotto il margine inferiore a (0, 5) per fare spazio al testo dell'IA
            ctk.CTkLabel(card, text=f"Response time: {tempo_risposta:.1f} sec", font=font_normale, text_color="#888888").pack(anchor="w", padx=10, pady=(0, 5))

            # =========================================================
            # 1. NUOVO: Spazio vuoto per il testo di Gemini
            # =========================================================
            rephrased_label = ctk.CTkLabel(card, text="", font=font_risposta, text_color=TEXT_GREEN, wraplength=850, justify="left")
            rephrased_label.pack(anchor="w", padx=10, pady=(0, 10))

            # =========================================================
            # 2. MODIFICATO: Bottone collegato alla vera IA
            # =========================================================
            btn_reformulate = ctk.CTkButton(card, text="Reformulate", font=font_bottoni, 
                                          fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER, 
                                          width=140, height=35, corner_radius=10)
            
            # Colleghiamo il bottone passando il testo, la nuova etichetta e il bottone stesso
            btn_reformulate.configure(command=lambda t=item['text'], lbl=rephrased_label, btn=btn_reformulate: self.handle_reformulate_click(t, lbl, btn))
            btn_reformulate.pack(anchor="w", padx=10, pady=(0, 20))

            # --- DA QUI IN POI CONTINUA NORMALMENTE ---
            stats_container = ctk.CTkFrame(card, fg_color="transparent")
            stats_container.pack(fill="x", padx=10, pady=5)
            canvas_w = 320
            canvas_h = 16

            v_count = item.get('vocal_fillers', 0)
            v_dict = item.get('vocal_fillers_dict', {})
            v_string = f"{v_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in v_dict.items()]) if v_count > 0 else "0"

            f_count = item.get('filler_words', 0)
            f_dict = item.get('filler_words_dict', {})
            f_string = f"{f_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in f_dict.items()]) if f_count > 0 else "0"

            # Modifica 2: Aggiunto pady=5 ai frame delle statistiche così hanno spazio per le curve
            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            cv_hand = cv_data.get("hand_gesture", {})

            # ---- SPEECH FRAME ----
            speech_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            speech_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            ctk.CTkLabel(speech_frame, text="🎤 Speech Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # 1. Chiamiamo la nuova funzione di calcolo
            report_speech = valuta_performance_speech(item)
            
            val_long = report_speech.get("long_pauses", {})
            val_micro = report_speech.get("micro_silences", {})
            val_vocal = report_speech.get("vocal_fillers", {})
            val_filler = report_speech.get("filler_words", {})
            val_tremor = report_speech.get("tremor", {})

            # 2. Inseriamo le statistiche con il pallino dinamico (add_dot)
            add_dot(speech_frame, f"Long Pauses: {val_long.get('valore_reale', 0)}", val_long)
            add_dot(speech_frame, f"Micro Silences: {val_micro.get('valore_reale', 0)}", val_micro)
            add_dot(speech_frame, f"Vocal Fillers: {val_vocal.get('valore_reale', 0)}", val_vocal)
            add_dot(speech_frame, f"Filler Words: {val_filler.get('valore_reale', 0)}", val_filler)
            add_dot(speech_frame, f"Voice Tremor: {val_tremor.get('valore_reale', 0):.0f} / 100", val_tremor)

            # 3. TOTAL SPEECH GRAVITY (Grassetto, Maiuscolo)
            ctk.CTkLabel(speech_frame, text="TOTAL SPEECH GRAVITY", font=font_titolo_box, text_color="#333333").pack(anchor="center", pady=(15, 5))

            # 4. Calcolo della gravità totale per lo speech (da 0 a 100)
            speech_gravity_raw = (
                val_tremor.get('valore_calcolato', 0) * 0.4 +               # Jitter al 40%
                val_long.get('valore_calcolato', 0) * 20 +                  # Pausa lunga: +20 punti
                val_micro.get('valore_calcolato', 0) * 1.5 +                # Micro silenzi: impatto leggero
                max(0, val_filler.get('valore_calcolato', 0) - 2) * 5 +     # Penalità se filler > 2
                abs(val_vocal.get('valore_calcolato', 0) - 3.5) * 5         # Penalità se troppo distanti dalla fascia verde (3.5)
            )
            speech_percent = int(max(0, min(100, speech_gravity_raw)))

            # 5. Barra colorata personalizzata
            bar_canvas_s = ctk.CTkCanvas(speech_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas_s.pack(anchor="center", pady=(0, 0))

            # Soglie per speech_gravity
            speech_gravity_soglie = (5.0, 30.0, 60.0, 85.0)
            segments_s = get_threshold_segments(canvas_w, canvas_h, speech_gravity_soglie)
            
            bar_canvas_s.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments_s[0][2], outline=segments_s[0][2])
            bar_canvas_s.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments_s[-1][2], outline=segments_s[-1][2])
            
            for x_start, x_end, color in segments_s:
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                if adjusted_end > adjusted_start:
                    bar_canvas_s.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # Lineetta nera indicatore
            marker_x_s = (speech_percent / 100) * canvas_w
            bar_canvas_s.create_line(marker_x_s, -2, marker_x_s, canvas_h + 10, fill="black", width=4)

            # Numero in percentuale sotto la barra
            ctk.CTkLabel(speech_frame, text=f"{speech_percent}%", font=font_titolo_box, text_color="black").pack(anchor="center", pady=(0, 5))
            
            
            # ---- GAZE/FACE FRAME ----
            face_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            face_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            cv_data = item.get("cv_data", {})
            
            # CHIAMIAMO SCORE_CV.PY PER AVERE TUTTI I DATI PRONTI E COLORATI
            report_cv = valuta_performance_cv(cv_data)
            
            val_eyes = report_cv.get("eye_gaze", {})
            val_head = report_cv.get("head_movement", {})
            val_down = report_cv.get("head_down", {})
            
            val_gest = report_cv.get("hand_general", {})
            val_touch = report_cv.get("face_touch", {})
            val_overlap = report_cv.get("face_overlap", {})
            val_tremor = report_cv.get("face_tremor", {})

            # 1. Titolo
            ctk.CTkLabel(face_frame, text="👁️ Gaze Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # 2 e 3. Eyes Distracted, Head Turn Time e Head Down
            # 2 e 3. Eyes Distracted, Head Turn Time e Head Down
            add_dot(face_frame, f"Eyes Distracted: {cv_face.get('eye_gaze_time', 0.0):.1f}s", val_eyes)
            add_dot(face_frame, f"Head Turn: {cv_face.get('head_movement_time', 0.0):.1f}s", val_head)
            add_dot(face_frame, f"Head Down: {cv_face.get('head_down', 0.0):.1f}s", val_down)
            add_dot(face_frame, f"Nodding: {cv_face.get('face_tremor_time', 0.0):.1f}s", val_tremor)

            # 4. TOTAL GAZE GRAVITY (Grassetto, Maiuscolo)
            ctk.CTkLabel(face_frame, text="TOTAL GAZE GRAVITY", font=font_titolo_box, text_color="#333333").pack(anchor="center", pady=(15, 5))

            # Estraiamo il valore come intero per la percentuale
            gaze_percent = int(cv_face.get('head_total', 0.0))
            gaze_percent_clamped = max(0, min(100, gaze_percent)) # Limita tra 0 e 100 per non far uscire la lineetta dal disegno
            
            # 5. Barra colorata personalizzata (utilizziamo un Canvas di Tkinter)
            canvas_w = 320
            canvas_h = 16
            bar_canvas = ctk.CTkCanvas(face_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas.pack(anchor="center", pady=(0, 0))

            # Soglie per head_total: (5.0, 25.0, 60.0, 85.0)
            head_total_soglie = (5.0, 25.0, 60.0, 85.0)
            segments = get_threshold_segments(canvas_w, canvas_h, head_total_soglie)
            
            # Disegniamo gli archi arrotondati ai due estremi
            bar_canvas.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments[0][2], outline=segments[0][2])
            bar_canvas.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments[-1][2], outline=segments[-1][2])
            
            # Disegniamo i segmenti
            for x_start, x_end, color in segments:
                # Aggiustiamo i margini per gli archi
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                
                if adjusted_end > adjusted_start:
                    bar_canvas.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # Lineetta nera indicatore
            marker_x = (gaze_percent_clamped / 100) * canvas_w
            bar_canvas.create_line(marker_x, -2, marker_x, canvas_h + 10, fill="black", width=4)

            # Numero in percentuale sotto la barra
            ctk.CTkLabel(face_frame, text=f"{gaze_percent}%", font=font_titolo_box, text_color="black").pack(anchor="center", pady=(0, 5))
            
            
            # ---- HAND FRAME ----
            hand_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            hand_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            # 1. Titolo
            ctk.CTkLabel(hand_frame, text="🖐️ Gesture Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # 2. Statistiche principali
            add_dot(hand_frame, f"Gesticulation: {cv_hand.get('hand_general_time', 0.0):.1f}s", val_gest)
            add_dot(hand_frame, f"Big gestures: {cv_hand.get('face_touch_time', 0.0):.1f}s", val_touch)
            add_dot(hand_frame, f"Touching Face: {cv_hand.get('face_overlap_time', 0.0):.1f}s", val_overlap)
            # 4. TOTAL GESTURE GRAVITY (Grassetto, Maiuscolo)
            ctk.CTkLabel(hand_frame, text="TOTAL GESTURE GRAVITY", font=font_titolo_box, text_color="#333333").pack(anchor="center", pady=(15, 5))

            # Estraiamo il valore come intero (tuo *100 è già in union_face_hands.py!)
            hand_percent = int(cv_hand.get('hand_gravity', 0.0))
            hand_percent_clamped = max(0, min(100, hand_percent))
            
            # 5. Barra colorata personalizzata (Riutilizziamo le misure del Gaze)
            bar_canvas_h = ctk.CTkCanvas(hand_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas_h.pack(anchor="center", pady=(0, 0))
            
            # Soglie per hand_gravity: (5.0, 35.0, 55.0, 80.0)
            hand_gravity_soglie = (5.0, 35.0, 55.0, 80.0)
            segments_h = get_threshold_segments(canvas_w, canvas_h, hand_gravity_soglie)
            
            # Disegniamo gli archi arrotondati ai due estremi
            bar_canvas_h.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments_h[0][2], outline=segments_h[0][2])
            bar_canvas_h.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments_h[-1][2], outline=segments_h[-1][2])
            
            # Disegniamo i segmenti
            for x_start, x_end, color in segments_h:
                # Aggiustiamo i margini per gli archi
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                
                if adjusted_end > adjusted_start:
                    bar_canvas_h.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # Lineetta nera indicatore
            marker_x_h = (hand_percent_clamped / 100) * canvas_w
            bar_canvas_h.create_line(marker_x_h, -2, marker_x_h, canvas_h + 10, fill="black", width=4)

            # Numero in percentuale sotto la barra
            ctk.CTkLabel(hand_frame, text=f"{hand_percent}%", font=font_titolo_box, text_color="black").pack(anchor="center", pady=(0, 5))
            ##################
            q_score_frame = ctk.CTkFrame(card, fg_color="transparent")
            q_score_frame.pack(pady=(15, 10), anchor="center")
            
            ctk.CTkLabel(q_score_frame, text="Score: ", font=font_titolo_box, text_color="#333333").pack(side="left")
            
           
            score_value = int((hand_percent_clamped + gaze_percent_clamped + speech_percent) / 3) # Semplice media dei 3 punteggi principali
            all_question_scores.append(score_value)  # Aggiungi il punteggio alla lista
            ctk.CTkLabel(q_score_frame, text=f" {score_value} / 100 ", font=font_domanda, 
                         fg_color=TEXT_GREEN, text_color="white", corner_radius=8, width=80, height=30).pack(side="left", padx=5)
            
            ########
        # =========================================================
        # 2. SECOND PART: OVERALL FEEDBACK AND SCORE
        # =========================================================
        ctk.CTkLabel(center_frame, text="Overall Feedback", font=font_titolo_sezione, text_color=TEXT_SUB).pack(anchor="w", pady=(40, 10), padx=20)
        
        feedback_frame = ctk.CTkFrame(center_frame, fg_color="white", corner_radius=15, border_width=2, border_color="#E8ECE8")
        feedback_frame.pack(fill="x", padx=20, pady=5, ipady=20, ipadx=20)

        # Calcola il punteggio finale come media di tutti i punteggi delle domande
        final_score_value = int(sum(all_question_scores) / len(all_question_scores)) if all_question_scores else 0 
        
        if final_score_value > 66:
            score_color = "#12BA4B" 
        elif final_score_value >= 33:
            score_color = "#FF9800" 
        else:
            score_color = "#F44336" 

        score_container = ctk.CTkFrame(feedback_frame, fg_color="transparent")
        # Modifica 1b: Anche qui aggiunto il margine in alto per non tagliare il bordo 
        score_container.pack(anchor="w", padx=10, pady=(20, 20))

        ctk.CTkLabel(score_container, text="Final Score: ", font=font_titolo_box, text_color="#333333").pack(side="left")
        
        ctk.CTkLabel(score_container, text=f" {final_score_value} / 100 ", font=font_domanda, 
                     fg_color=score_color, text_color="white", corner_radius=8, width=100, height=35).pack(side="left", padx=10)

        ctk.CTkLabel(feedback_frame, text="Questions to Review:", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="w", padx=10)
        
        review_text = get_questions_to_review(data)
        ctk.CTkLabel(feedback_frame, text=review_text, 
                     font=font_normale, text_color="#333333", justify="left", wraplength=850).pack(anchor="w", padx=20, pady=(5, 20))
        
        ctk.CTkLabel(feedback_frame, text="Suggestions:", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="w", padx=10)
        
        # Genera suggestions dinamiche basate sui dati
        suggestions_list = generate_suggestions(data)
        
        if suggestions_list:
            for suggestion_text, color in suggestions_list:
                # Crea un frame per ogni suggestion con pallino colorato
                sugg_row = ctk.CTkFrame(feedback_frame, fg_color="transparent")
                sugg_row.pack(anchor="w", padx=20, pady=2)
                
                # Pallino colorato
                pallino_symbol = "●"
                ctk.CTkLabel(sugg_row, text=f"{pallino_symbol} ", font=font_normale, text_color=color).pack(side="left")
                
                # Testo suggestion
                ctk.CTkLabel(sugg_row, text=suggestion_text, font=font_normale, text_color="#333333", wraplength=800, justify="left").pack(side="left", fill="both", expand=True)
        else:
            # Fallback se non ci sono suggestions
            ctk.CTkLabel(feedback_frame, text="No specific suggestions at this time.", 
                         font=font_normale, text_color="#888888").pack(anchor="w", padx=20, pady=5)

        # =========================================================
        # DOWNLOAD BUTTON
        # =========================================================
        
        ctk.CTkButton(center_frame, text="Download Report", font=font_bottoni, 
                      fg_color=TEXT_GREEN, text_color="white", hover_color=TEXT_SUB, 
                      width=250, height=55, corner_radius=15,
                      command=lambda: self.export_report(data, final_score_value)).pack(pady=(50, 20))


    def export_report(self, data, final_score):
        # 1. Chiedi all'utente dove vuole salvare il file 
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
            title="Save Interview Report",
            initialfile="Interview_Report.txt"
        )
        
        if not file_path:
            return

        # 2. Genera l'intero testo richiamando la funzione del file utils.py
        testo_report = generate_report_text(data, final_score)

        # 3. Scrive tutto nel file prescelto 
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(testo_report)
            print(f"Report scaricato con successo in: {file_path}") 
        except Exception as e:
            print(f"Errore durante il salvataggio del report: {e}") 

    def handle_reformulate_click(self, original_text, rephrased_label_widget, button_widget):
        # 1. Il bottone diventa grigio e dice "Thinking..."
        button_widget.configure(state="disabled", text="Thinking...", text_color="gray")

        # 2. Task in background
        def background_task():
            # Richiamiamo l'IA da ai_helper.py
            rephrased_text = get_reformulated_text(original_text)
            
            if rephrased_text:
                # Se ha successo, INSERIAMO IL TESTO NELLO SPAZIO VUOTO!
                self.after(0, lambda: rephrased_label_widget.configure(
                    text=f"✨ Suggested: \"{rephrased_text}\""
                ))
                # Disabilitiamo il bottone in modo definitivo per evitare che l'utente clicchi 10 volte
                self.after(0, lambda: button_widget.configure(text="Reformulated!", fg_color="#E0E0E0", state="disabled"))
            else:
                # Se fallisce, permettiamo di riprovare
                self.after(0, lambda: button_widget.configure(state="normal", text="Error. Try again", text_color="red"))

        # 3. Avviamo il thread
        threading.Thread(target=background_task, daemon=True).start()

'''
# screens/screen5.py
import customtkinter as ctk
from utils import (
    generate_report_text,
    DEFAULT_INTERVIEW_DATA,
    add_dot
)  
from tkinter import filedialog
from score import valuta_performance_cv, valuta_performance_speech
from config import (
    CARD_BG, 
    CARD_BORDER, 
    TEXT_GREEN,
    TEXT_SUB,
    BTN_BG, 
    BTN_TEXT, 
    BTN_HOVER,
    APP_FONT
)
import threading
from ai_helper import get_reformulated_text # Importiamo la nostra IA!

def get_threshold_segments(canvas_w, canvas_h, soglie):
    """
    Genera i segmenti di una barra colorata basati su soglie percentuali.
    Ritorna una lista di (x_start, x_end, color)
    """
    min_rosso, min_giallo, max_giallo, max_rosso = soglie
    color_rosso = "#F44336"
    color_arancione = "#FF9800"
    color_verde = "#4CAF50"
    
    segments = []
    
    # Converti percentuali in pixel
    def pct_to_px(pct):
        return (pct / 100.0) * canvas_w
    
    threshold_points = [0, min_rosso, min_giallo, max_giallo, max_rosso, 100]
    threshold_colors = [color_rosso, color_arancione, color_verde, color_arancione, color_rosso]
    
    for i in range(len(threshold_points) - 1):
        x_start = pct_to_px(threshold_points[i])
        x_end = pct_to_px(threshold_points[i + 1])
        color = threshold_colors[i]
        
        if x_end > x_start:  # Solo se il segmento ha larghezza
            segments.append((x_start, x_end, color))
    
    return segments

class Screen5(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.pack(expand=True, fill="both") 
        
        # DEFINIZIONE DEI FONT
        font_titolo_grande = ctk.CTkFont(family=APP_FONT, size=34, weight="bold")
        font_titolo_sezione = ctk.CTkFont(family=APP_FONT, size=24, weight="bold")
        font_domanda = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")
        font_risposta = ctk.CTkFont(family=APP_FONT, size=15, slant="italic")
        font_titolo_box = ctk.CTkFont(family=APP_FONT, size=16, weight="bold")
        font_normale = ctk.CTkFont(family=APP_FONT, size=14)
        font_bottoni = ctk.CTkFont(family=APP_FONT, size=16, weight="bold")

        # CONTAINER INTERNO (Card principale)
        center_frame = ctk.CTkFrame(self, 
                                    fg_color=CARD_BG, 
                                    border_color=CARD_BORDER, 
                                    border_width=5, 
                                    corner_radius=20)
        center_frame.pack(pady=40, padx=40, ipadx=40, ipady=40, expand=True, fill="both")

        # TITLE SECTION 
        # Modifica 1: Aggiunto pady=40 anche sopra per non tagliare il bordo della card!
        ctk.CTkLabel(center_frame, text="Interview Report", font=font_titolo_grande, text_color=TEXT_GREEN).pack(anchor="center", pady=(40, 40))

        # Se non arrivano dati reali dall'intervista, carica il mock dal file utils
        if not data:
            data = DEFAULT_INTERVIEW_DATA

        # =========================================================
        # 1. FIRST PART: QUESTION BY QUESTION REPORT
        # =========================================================
        ctk.CTkLabel(center_frame, text="Questions & Answers Analysis", font=font_titolo_sezione, text_color=TEXT_SUB).pack(anchor="w", pady=(10, 20), padx=20)


        for idx, item in enumerate(data):
            card = ctk.CTkFrame(center_frame, fg_color="white", corner_radius=15, border_width=2, border_color="#E8ECE8")
            card.pack(fill="x", pady=15, padx=20, ipady=15, ipadx=15)

            ctk.CTkLabel(card, text=f"Q{idx+1}: {item['question']}", font=font_domanda, text_color=TEXT_GREEN, wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(card, text=f"Your answer: \"{item['text']}\"", font=font_risposta, text_color="#555555", wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(0, 5))
            
            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            tempo_risposta = cv_face.get("tempo_totale_risposta", 0.0)
            
            ctk.CTkLabel(card, text=f"Response time: {tempo_risposta:.1f} sec", font=font_normale, text_color="#888888").pack(anchor="w", padx=10, pady=(0, 5))

            # =========================================================
            # 1. LA PARTE MANCANTE: Spazio vuoto per il testo di Gemini
            # =========================================================
            rephrased_label = ctk.CTkLabel(card, text="", font=font_risposta, text_color=TEXT_GREEN, wraplength=850, justify="left")
            rephrased_label.pack(anchor="w", padx=10, pady=(0, 10))

            # =========================================================
            # 2. LA PARTE MANCANTE: Bottone collegato alla vera IA
            # =========================================================
            btn_reformulate = ctk.CTkButton(card, text="Reformulate", font=font_bottoni, 
                                          fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER, 
                                          width=140, height=35, corner_radius=10)
            
            # Colleghiamo il bottone alla funzione handle_reformulate_click
            btn_reformulate.configure(command=lambda t=item['text'], lbl=rephrased_label, btn=btn_reformulate: self.handle_reformulate_click(t, lbl, btn))
            btn_reformulate.pack(anchor="w", padx=10, pady=(0, 20))


            stats_container = ctk.CTkFrame(card, fg_color="transparent")
            stats_container.pack(fill="x", padx=10, pady=5)
            canvas_w = 320
            canvas_h = 16

            v_count = item.get('vocal_fillers', 0)
            v_dict = item.get('vocal_fillers_dict', {})
            v_string = f"{v_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in v_dict.items()]) if v_count > 0 else "0"

            f_count = item.get('filler_words', 0)
            f_dict = item.get('filler_words_dict', {})
            f_string = f"{f_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in f_dict.items()]) if f_count > 0 else "0"

            # Modifica 2: Aggiunto pady=5 ai frame delle statistiche così hanno spazio per le curve
            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            cv_hand = cv_data.get("hand_gesture", {})

            # ---- SPEECH FRAME ----
            speech_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            speech_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            ctk.CTkLabel(speech_frame, text="🎤 Speech Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # 1. Chiamiamo la nuova funzione di calcolo
            report_speech = valuta_performance_speech(item)
            
            val_long = report_speech.get("long_pauses", {})
            val_micro = report_speech.get("micro_silences", {})
            val_vocal = report_speech.get("vocal_fillers", {})
            val_filler = report_speech.get("filler_words", {})
            val_tremor = report_speech.get("tremor", {})

            # 2. Inseriamo le statistiche con il pallino dinamico (add_dot)
            add_dot(speech_frame, f"Long Pauses: {val_long.get('valore_reale', 0)}", val_long)
            add_dot(speech_frame, f"Micro Silences: {val_micro.get('valore_reale', 0)}", val_micro)
            add_dot(speech_frame, f"Vocal Fillers: {val_vocal.get('valore_reale', 0)}", val_vocal)
            add_dot(speech_frame, f"Filler Words: {val_filler.get('valore_reale', 0)}", val_filler)
            add_dot(speech_frame, f"Voice Tremor: {val_tremor.get('valore_reale', 0):.0f} / 100", val_tremor)

            # 3. TOTAL SPEECH GRAVITY (Grassetto, Maiuscolo)
            ctk.CTkLabel(speech_frame, text="TOTAL SPEECH GRAVITY", font=font_titolo_box, text_color="#333333").pack(anchor="center", pady=(15, 5))

            # 4. Calcolo della gravità totale per lo speech (da 0 a 100)
            speech_gravity_raw = (
                val_tremor.get('valore_calcolato', 0) * 0.4 +               # Jitter al 40%
                val_long.get('valore_calcolato', 0) * 20 +                  # Pausa lunga: +20 punti
                val_micro.get('valore_calcolato', 0) * 1.5 +                # Micro silenzi: impatto leggero
                max(0, val_filler.get('valore_calcolato', 0) - 2) * 5 +     # Penalità se filler > 2
                abs(val_vocal.get('valore_calcolato', 0) - 3.5) * 5         # Penalità se troppo distanti dalla fascia verde (3.5)
            )
            speech_percent = int(max(0, min(100, speech_gravity_raw)))

            # 5. Barra colorata personalizzata
            bar_canvas_s = ctk.CTkCanvas(speech_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas_s.pack(anchor="center", pady=(0, 0))

            # Soglie per speech_gravity
            speech_gravity_soglie = (5.0, 30.0, 60.0, 85.0)
            segments_s = get_threshold_segments(canvas_w, canvas_h, speech_gravity_soglie)
            
            bar_canvas_s.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments_s[0][2], outline=segments_s[0][2])
            bar_canvas_s.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments_s[-1][2], outline=segments_s[-1][2])
            
            for x_start, x_end, color in segments_s:
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                if adjusted_end > adjusted_start:
                    bar_canvas_s.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # Lineetta nera indicatore
            marker_x_s = (speech_percent / 100) * canvas_w
            bar_canvas_s.create_line(marker_x_s, -2, marker_x_s, canvas_h + 10, fill="black", width=4)

            # Numero in percentuale sotto la barra
            ctk.CTkLabel(speech_frame, text=f"{speech_percent}%", font=font_titolo_box, text_color="black").pack(anchor="center", pady=(0, 5))
            
            
            # ---- GAZE/FACE FRAME ----
            face_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            face_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            cv_data = item.get("cv_data", {})
            
            # CHIAMIAMO SCORE_CV.PY PER AVERE TUTTI I DATI PRONTI E COLORATI
            report_cv = valuta_performance_cv(cv_data)
            
            val_eyes = report_cv.get("eye_gaze", {})
            val_head = report_cv.get("head_movement", {})
            val_down = report_cv.get("head_down", {})
            
            val_gest = report_cv.get("hand_general", {})
            val_touch = report_cv.get("face_touch", {})
            val_overlap = report_cv.get("face_overlap", {})
            val_tremor = report_cv.get("face_tremor", {})

            # 1. Titolo
            ctk.CTkLabel(face_frame, text="👁️ Gaze Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # 2 e 3. Eyes Distracted, Head Turn Time e Head Down
            # 2 e 3. Eyes Distracted, Head Turn Time e Head Down
            add_dot(face_frame, f"Eyes Distracted: {cv_face.get('eye_gaze_time', 0.0):.1f}s", val_eyes)
            add_dot(face_frame, f"Head Turn: {cv_face.get('head_movement_time', 0.0):.1f}s", val_head)
            add_dot(face_frame, f"Head Down: {cv_face.get('head_down', 0.0):.1f}s", val_down)
            add_dot(face_frame, f"Nodding: {cv_face.get('face_tremor_time', 0.0):.1f}s", val_tremor)

            # 4. TOTAL GAZE GRAVITY (Grassetto, Maiuscolo)
            ctk.CTkLabel(face_frame, text="TOTAL GAZE GRAVITY", font=font_titolo_box, text_color="#333333").pack(anchor="center", pady=(15, 5))

            # Estraiamo il valore come intero per la percentuale
            gaze_percent = int(cv_face.get('head_total', 0.0))
            gaze_percent_clamped = max(0, min(100, gaze_percent)) # Limita tra 0 e 100 per non far uscire la lineetta dal disegno
            
            # 5. Barra colorata personalizzata (utilizziamo un Canvas di Tkinter)
            canvas_w = 320
            canvas_h = 16
            bar_canvas = ctk.CTkCanvas(face_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas.pack(anchor="center", pady=(0, 0))

            # Soglie per head_total: (5.0, 25.0, 60.0, 85.0)
            head_total_soglie = (5.0, 25.0, 60.0, 85.0)
            segments = get_threshold_segments(canvas_w, canvas_h, head_total_soglie)
            
            # Disegniamo gli archi arrotondati ai due estremi
            bar_canvas.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments[0][2], outline=segments[0][2])
            bar_canvas.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments[-1][2], outline=segments[-1][2])
            
            # Disegniamo i segmenti
            for x_start, x_end, color in segments:
                # Aggiustiamo i margini per gli archi
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                
                if adjusted_end > adjusted_start:
                    bar_canvas.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # Lineetta nera indicatore
            marker_x = (gaze_percent_clamped / 100) * canvas_w
            bar_canvas.create_line(marker_x, -2, marker_x, canvas_h + 10, fill="black", width=4)

            # Numero in percentuale sotto la barra
            ctk.CTkLabel(face_frame, text=f"{gaze_percent}%", font=font_titolo_box, text_color="black").pack(anchor="center", pady=(0, 5))
            
            
            # ---- HAND FRAME ----
            hand_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            hand_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            # 1. Titolo
            ctk.CTkLabel(hand_frame, text="🖐️ Gesture Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # 2. Statistiche principali
            add_dot(hand_frame, f"Gesticulation: {cv_hand.get('hand_general_time', 0.0):.1f}s", val_gest)
            add_dot(hand_frame, f"Big gestures: {cv_hand.get('face_touch_time', 0.0):.1f}s", val_touch)
            add_dot(hand_frame, f"Touching Face: {cv_hand.get('face_overlap_time', 0.0):.1f}s", val_overlap)
            # 4. TOTAL GESTURE GRAVITY (Grassetto, Maiuscolo)
            ctk.CTkLabel(hand_frame, text="TOTAL GESTURE GRAVITY", font=font_titolo_box, text_color="#333333").pack(anchor="center", pady=(15, 5))

            # Estraiamo il valore come intero (tuo *100 è già in union_face_hands.py!)
            hand_percent = int(cv_hand.get('hand_gravity', 0.0))
            hand_percent_clamped = max(0, min(100, hand_percent))
            
            # 5. Barra colorata personalizzata (Riutilizziamo le misure del Gaze)
            bar_canvas_h = ctk.CTkCanvas(hand_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas_h.pack(anchor="center", pady=(0, 0))
            
            # Soglie per hand_gravity: (5.0, 35.0, 55.0, 80.0)
            hand_gravity_soglie = (5.0, 35.0, 55.0, 80.0)
            segments_h = get_threshold_segments(canvas_w, canvas_h, hand_gravity_soglie)
            
            # Disegniamo gli archi arrotondati ai due estremi
            bar_canvas_h.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments_h[0][2], outline=segments_h[0][2])
            bar_canvas_h.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments_h[-1][2], outline=segments_h[-1][2])
            
            # Disegniamo i segmenti
            for x_start, x_end, color in segments_h:
                # Aggiustiamo i margini per gli archi
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                
                if adjusted_end > adjusted_start:
                    bar_canvas_h.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # Lineetta nera indicatore
            marker_x_h = (hand_percent_clamped / 100) * canvas_w
            bar_canvas_h.create_line(marker_x_h, -2, marker_x_h, canvas_h + 10, fill="black", width=4)

            # Numero in percentuale sotto la barra
            ctk.CTkLabel(hand_frame, text=f"{hand_percent}%", font=font_titolo_box, text_color="black").pack(anchor="center", pady=(0, 5))
            ##################
            q_score_frame = ctk.CTkFrame(card, fg_color="transparent")
            q_score_frame.pack(pady=(15, 10), anchor="center")
            
            ctk.CTkLabel(q_score_frame, text="Score: ", font=font_titolo_box, text_color="#333333").pack(side="left")
            ctk.CTkLabel(q_score_frame, text=" 80 / 100 ", font=font_domanda, 
                         fg_color=TEXT_GREEN, text_color="white", corner_radius=8, width=80, height=30).pack(side="left", padx=5)
            
            ########
        # =========================================================
        # 2. SECOND PART: OVERALL FEEDBACK AND SCORE
        # =========================================================
        ctk.CTkLabel(center_frame, text="Overall Feedback", font=font_titolo_sezione, text_color=TEXT_SUB).pack(anchor="w", pady=(40, 10), padx=20)
        
        feedback_frame = ctk.CTkFrame(center_frame, fg_color="white", corner_radius=15, border_width=2, border_color="#E8ECE8")
        feedback_frame.pack(fill="x", padx=20, pady=5, ipady=20, ipadx=20)

        final_score_value = 75 
        
        if final_score_value > 66:
            score_color = "#12BA4B" 
        elif final_score_value >= 33:
            score_color = "#FF9800" 
        else:
            score_color = "#F44336" 

        score_container = ctk.CTkFrame(feedback_frame, fg_color="transparent")
        # Modifica 1b: Anche qui aggiunto il margine in alto per non tagliare il bordo 
        score_container.pack(anchor="w", padx=10, pady=(20, 20))

        ctk.CTkLabel(score_container, text="Final Score: ", font=font_titolo_box, text_color="#333333").pack(side="left")
        
        ctk.CTkLabel(score_container, text=f" {final_score_value} / 100 ", font=font_domanda, 
                     fg_color=score_color, text_color="white", corner_radius=8, width=100, height=35).pack(side="left", padx=10)

        ctk.CTkLabel(feedback_frame, text="Questions to Review:", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(feedback_frame, text="• Q2: What is your greatest weakness? (High voice tremor detected)\n• Q4: Where do you see yourself in 5 years? (Too many filler words)", 
                     font=font_normale, text_color="#333333", justify="left", wraplength=850).pack(anchor="w", padx=20, pady=(5, 20))

        ctk.CTkLabel(feedback_frame, text="Suggestions:", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="w", padx=10)
        
        ctk.CTkLabel(feedback_frame, text="🟢 Positive: Your gaze was very steady and you maintained good eye contact.\n🟢 Positive: You didn't touch your face and used hand gestures effectively to explain yourself.\n🔴 Negative: Your voice trembled significantly during some answers, try taking deep breaths.\n🔴 Negative: Try to reduce filler words like 'basically' and 'like'.", 
                     font=font_normale, text_color="#333333", justify="left", wraplength=850).pack(anchor="w", padx=20, pady=(5, 10))

        # =========================================================
        # DOWNLOAD BUTTON
        # =========================================================
        
        ctk.CTkButton(center_frame, text="Download Report", font=font_bottoni, 
                      fg_color=TEXT_GREEN, text_color="white", hover_color=TEXT_SUB, 
                      width=250, height=55, corner_radius=15,
                      command=lambda: self.export_report(data, final_score_value)).pack(pady=(50, 20))


    def export_report(self, data, final_score):
        # 1. Chiedi all'utente dove vuole salvare il file 
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
            title="Save Interview Report",
            initialfile="Interview_Report.txt"
        )
        
        if not file_path:
            return

        # 2. Genera l'intero testo richiamando la funzione del file utils.py
        testo_report = generate_report_text(data, final_score)

        # 3. Scrive tutto nel file prescelto 
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(testo_report)
            print(f"Report scaricato con successo in: {file_path}") 
        except Exception as e:
            print(f"Errore durante il salvataggio del report: {e}") 

    def handle_reformulate_click(self, original_text, rephrased_label_widget, button_widget):
        # 1. Il bottone diventa grigio e dice "Thinking..."
        button_widget.configure(state="disabled", text="Thinking...", text_color="gray")

        # 2. Task in background
        def background_task():
            # Richiamiamo l'IA da ai_helper.py
            rephrased_text = get_reformulated_text(original_text)
            
            if rephrased_text:
                # Se ha successo, INSERIAMO IL TESTO NELLO SPAZIO VUOTO!
                self.after(0, lambda: rephrased_label_widget.configure(
                    text=f"✨ Suggested: \"{rephrased_text}\""
                ))
                # Disabilitiamo il bottone in modo definitivo per evitare che l'utente clicchi 10 volte
                self.after(0, lambda: button_widget.configure(text="Reformulated!", fg_color="#E0E0E0", state="disabled"))
            else:
                # Se fallisce, permettiamo di riprovare
                self.after(0, lambda: button_widget.configure(state="normal", text="Error. Try again", text_color="red"))

        # 3. Avviamo il thread
        threading.Thread(target=background_task, daemon=True).start()'''