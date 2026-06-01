# screens/screen5.py
import customtkinter as ctk
from utils import generate_report_text  
from utils import DEFAULT_INTERVIEW_DATA  #dati fittizzi per il mock del report, se non arrivano dati reali dall'intervista
from tkinter import filedialog
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
            
            ctk.CTkLabel(card, text=f"Your answer: \"{item['text']}\"", font=font_risposta, text_color="#555555", wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(0, 15))

            ctk.CTkButton(card, text="Reformulate", font=font_bottoni, 
                          fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER, 
                          width=140, height=35, corner_radius=10,
                          command=lambda q=idx: print(f"Reformulating question {q+1}...")).pack(anchor="w", padx=10, pady=(0, 20))

            stats_container = ctk.CTkFrame(card, fg_color="transparent")
            stats_container.pack(fill="x", padx=10, pady=5)

            v_count = item.get('vocal_fillers', 0)
            v_dict = item.get('vocal_fillers_dict', {})
            v_string = f"{v_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in v_dict.items()]) if v_count > 0 else "0"

            f_count = item.get('filler_words', 0)
            f_dict = item.get('filler_words_dict', {})
            f_string = f"{f_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in f_dict.items()]) if f_count > 0 else "0"

            # Modifica 2: Aggiunto pady=5 ai frame delle statistiche così hanno spazio per le curve
            # ---- SPEECH FRAME ----
            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            cv_hand = cv_data.get("hand_gesture", {})

            speech_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20) # Angoli più arrotondati
            speech_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15) # Più spazio dai bordi
            
            ctk.CTkLabel(speech_frame, text="🎤 Speech Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            ctk.CTkLabel(speech_frame, text=f"Long Pauses: {item.get('silence_count', 0)}", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)
            ctk.CTkLabel(speech_frame, text=f"Vocal Fillers: {v_string}", font=font_normale, text_color="#333333", justify="center").pack(anchor="center", pady=4)
            ctk.CTkLabel(speech_frame, text=f"Filler Words: {f_string}", font=font_normale, text_color="#333333", justify="center").pack(anchor="center", pady=4)
            ctk.CTkLabel(speech_frame, text=f"Voice Tremor: {item.get('tremor', 0)} / 100", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)

            # ---- GAZE/FACE FRAME ----
            face_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            face_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            ctk.CTkLabel(face_frame, text="👁️ Gaze Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            ctk.CTkLabel(face_frame, text=f"Face Movements: {cv_face.get('head_total', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)            
            ctk.CTkLabel(face_frame, text=f"Eyes Distracted: {cv_face.get('eye_gaze_time', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)
            ctk.CTkLabel(face_frame, text=f"Face Tremor: {cv_face.get('face_tremor_time', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)
            ctk.CTkLabel(face_frame, text=f"Head Turn Time: {cv_face.get('head_movement_time', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)

            # ---- HAND FRAME ----
            hand_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            hand_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            ctk.CTkLabel(hand_frame, text="🖐️ Gesture Analysis", font=font_titolo_box, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            ctk.CTkLabel(hand_frame, text=f"Total Gesture: {cv_hand.get('hand_gravity', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)
            ctk.CTkLabel(hand_frame, text=f"Gesticulation: {cv_hand.get('hand_general_time', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)
            ctk.CTkLabel(hand_frame, text=f"Hands > Chin: {cv_hand.get('face_touch_time', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)
            ctk.CTkLabel(hand_frame, text=f"Touching Face: {cv_hand.get('face_overlap_time', 0.0):.1f}s", font=font_normale, text_color="#333333").pack(anchor="center", pady=4)
            # Modifica 3: Aggiunta la sezione "Score" per la singola domanda
            q_score_frame = ctk.CTkFrame(card, fg_color="transparent")
            q_score_frame.pack(pady=(15, 10), anchor="center")
            
            ctk.CTkLabel(q_score_frame, text="Score: ", font=font_titolo_box, text_color="#333333").pack(side="left")
            ctk.CTkLabel(q_score_frame, text=" 80 / 100 ", font=font_domanda, 
                         fg_color=TEXT_GREEN, text_color="white", corner_radius=8, width=80, height=30).pack(side="left", padx=5)


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

        # 3. Scrive tutto nel file prescelto [cite: 43]
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(testo_report)
            print(f"Report scaricato con successo in: {file_path}") 
        except Exception as e:
            print(f"Errore durante il salvataggio del report: {e}") 