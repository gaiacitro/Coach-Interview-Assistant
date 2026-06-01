# screens/screen2_3.py
import customtkinter as ctk
import random
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

class Screen2_3(ctk.CTkFrame):
    def __init__(self, parent, controller, mode="job"):
        super().__init__(parent, 
                         fg_color=CARD_BG, 
                         border_color=CARD_BORDER, 
                         border_width=5, 
                         corner_radius=20)
        self.controller = controller
        
        # Centra la card. I margini interni ora li diamo ai singoli elementi
        self.pack(expand=True, padx=20, pady=20)

        # Inizializza i font
        font_titolo = ctk.CTkFont(family=APP_FONT, size=28, weight="bold")
        font_label = ctk.CTkFont(family=APP_FONT, size=16, weight="bold")
        font_normale = ctk.CTkFont(family=APP_FONT, size=14)
        font_bottoni = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")

        self.checkboxes = []

        title_text = "Job Interview Practice" if mode == "job" else "University Oral Exam Practice"
        num_q_text = "Number of questions you want in the interview:" if mode == "job" else "Number of questions you want in the exam:"
        list_text = "Select the questions you would like to receive:" if mode == "job" else "Select or add the questions for your exam:"

        # 1 e 2. TITOLO: pady=(40, 20) stacca il testo dal bordo superiore, impedendo che si sovrapponga alla linea!
        ctk.CTkLabel(self, text=title_text, 
                     font=font_titolo, text_color=TEXT_GREEN).pack(pady=(40, 25), anchor="center")

        # INPUT NUMERO DOMANDE (con padx=40 per distanziarlo dai bordi laterali)
        ctk.CTkLabel(self, text=num_q_text, 
                     font=font_label, text_color=TEXT_SUB).pack(anchor="w", padx=40)
        
        self.num_questions = ctk.CTkEntry(self, placeholder_text="e.g. 5", height=45, corner_radius=10,
                                          font=font_normale, border_color=CARD_BORDER, text_color="black")
        self.num_questions.pack(fill="x", padx=40, pady=(5, 20))

        # LISTA DOMANDE
        ctk.CTkLabel(self, text=list_text, 
                     font=font_label, text_color=TEXT_SUB).pack(anchor="w", padx=40, pady=(0, 5))

        # FRAME SCROLLABILE: definisce la larghezza visiva interna della card
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=200, width=550)
        self.scroll_frame.pack(fill="x", padx=40, pady=5)

        if mode == "job":
            default_questions = [
                "Tell me about yourself",
                "What are your greatest strengths?",
                "What is your greatest weakness?",
                "Why do you want to work for this company?",
                "Where do you see yourself in five years?",
                "How do you handle pressure or stressful situations?",
                "Describe a difficult work situation and how you overcame it",
                "Why should we hire you?"
            ]
            for q in default_questions:
                self.add_checkbox(q)

        # 4. CASELLA DI TESTO CUSTOM: Nessun fill="x", usiamo larghezze fisse e la centriamo
        custom_frame = ctk.CTkFrame(self, fg_color="transparent")
        custom_frame.pack(pady=(15, 5), anchor="center")

        # Fissata la larghezza a 400 per renderla più stretta e proporzionata
        self.custom_entry = ctk.CTkEntry(custom_frame, placeholder_text="Type a custom question here...", 
                                         height=40, width=400,
                                         font=font_normale, border_color=CARD_BORDER, text_color="black")
        self.custom_entry.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(custom_frame, text="+ Add", width=80, height=40, 
                                fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER, 
                                font=font_label, corner_radius=10,
                                command=self.add_custom_question)
        add_btn.pack(side="right")

        # Label Errori
        self.error_label = ctk.CTkLabel(self, text="", text_color="red", font=font_label)
        self.error_label.pack(pady=(5, 5))

        # 3. BOTTONE START: Più piccolo (width=250), centrato e con spazio dal bordo inferiore (pady 40)
        submit_btn = ctk.CTkButton(
            self, text="Start the interview", font=font_bottoni, 
            fg_color=TEXT_GREEN, text_color=CARD_BG, height=50, width=250, corner_radius=15, 
            hover_color=TEXT_SUB, 
            command=self.validate_and_start
        )
        submit_btn.pack(pady=(5, 40), anchor="center")

    def add_checkbox(self, text):
        cb = ctk.CTkCheckBox(self.scroll_frame, text=text, font=ctk.CTkFont(family=APP_FONT, size=14), 
                             fg_color=TEXT_GREEN, hover_color=TEXT_SUB, border_color=CARD_BORDER, border_width=2,
                             text_color="#333333") 
        cb.pack(anchor="w", pady=8, padx=5)
        
        self.checkboxes.append(cb)

    def add_custom_question(self):
        text = self.custom_entry.get()
        if text.strip():
            self.add_checkbox(text)
            self.custom_entry.delete(0, 'end')

    def validate_and_start(self):
        # 1. Controlla se il campo del numero è vuoto o contiene testo non valido
        num_str = self.num_questions.get().strip()
        if not num_str:
            self.error_label.configure(text="Error: Please enter the number of questions.")
            return

        try:
            num_requested = int(num_str)
            if num_requested <= 0:
                self.error_label.configure(text="Error: The number must be greater than 0.")
                return
        except ValueError:
            self.error_label.configure(text="Error: Please enter a valid number (e.g. 3).")
            return

        # 2. Raccoglie tutte le domande che hanno la spunta
        selected_questions = []
        for cb in self.checkboxes:
            if cb.get() == 1: 
                selected_questions.append(cb.cget("text"))

        # 3. Controlla se le domande selezionate sono sufficienti
        if len(selected_questions) < num_requested:
            self.error_label.configure(
                text=f"Error: You requested {num_requested} questions, but selected only {len(selected_questions)}."
            )
            return

        # 4. Estrae casualmente il numero di domande richieste
        final_questions = random.sample(selected_questions, num_requested)

        # 5. Se è tutto ok, svuota eventuali errori vecchi e avvia l'intervista
        self.error_label.configure(text="")
        
        self.controller.show_screen("LoadingInterview", data=final_questions)