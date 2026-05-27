# screens/screen2_3.py
import customtkinter as ctk
import random
from config import PRINCIPAL_COLOR, SECONDARY_COLOR

class Screen2_3(ctk.CTkFrame):
    def __init__(self, parent, controller, mode="job"):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.pack(expand=True, fill="both", padx=40, pady=40)

        # --- NOVITÀ: Lista per tenere traccia delle checkbox create ---
        self.checkboxes = []

        # Determina i testi in base alla modalità ("job" o "uni")
        title_text = "Job Interview Practice" if mode == "job" else "University Oral Exam Practice"
        num_q_text = "Number of questions you want in the interview" if mode == "job" else "Number of questions you want in the exam"
        list_text = "Select the questions you would like to receive" if mode == "job" else "Select or add the questions for your exam"

        # Titolo
        ctk.CTkLabel(self, text=title_text, 
                     font=("Helvetica", 28, "bold"), text_color="black").pack(anchor="w", pady=(0, 20))

        # Input numero domande
        ctk.CTkLabel(self, text=num_q_text, 
                     font=("Helvetica", 16, "bold"), text_color="#000000").pack(anchor="w")
        
        self.num_questions = ctk.CTkEntry(self, placeholder_text="e.g. 5", height=45, corner_radius=10)
        self.num_questions.pack(fill="x", pady=(5, 20))

        # Lista domande
        ctk.CTkLabel(self, text=list_text, 
                     font=("Helvetica", 16, "bold"), text_color="#000000").pack(anchor="w", pady=(0, 10))

        # Frame scrollabile per le domande
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", height=300)
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

        # Carica domande di default solo se è una job interview
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

        # Sezione "New custom question"
        custom_frame = ctk.CTkFrame(self, fg_color="transparent")
        custom_frame.pack(fill="x", pady=10)

        self.custom_entry = ctk.CTkEntry(custom_frame, placeholder_text="Type a custom question here...", height=40)
        self.custom_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        add_btn = ctk.CTkButton(custom_frame, text="+ Add", width=80, height=40, fg_color=PRINCIPAL_COLOR, 
                                text_color="black", hover_color=SECONDARY_COLOR, command=self.add_custom_question)
        add_btn.pack(side="right")

        # --- NOVITÀ: Label per mostrare gli errori in rosso (inizialmente vuota) ---
        self.error_label = ctk.CTkLabel(self, text="", text_color="red", font=("Helvetica", 14, "bold"))
        self.error_label.pack(pady=(5, 0))

        # Bottone Invia (Ora richiama la funzione di validazione invece di passare subito alla schermata 4)
        submit_btn = ctk.CTkButton(
            self, text="Start the interview", font=("Helvetica", 18, "bold"), 
            fg_color=PRINCIPAL_COLOR, text_color="black", height=60, corner_radius=15,
            hover_color=SECONDARY_COLOR, 
            command=self.validate_and_start
        )
        submit_btn.pack(fill="x", pady=(10, 0))

    def add_checkbox(self, text):
        cb = ctk.CTkCheckBox(self.scroll_frame, text=text, font=("Helvetica", 13), 
                             fg_color=PRINCIPAL_COLOR, hover_color=SECONDARY_COLOR, border_color="gray", border_width=2)
        cb.pack(anchor="w", pady=8, padx=10)
        
        # Salviamo l'oggetto checkbox nella nostra lista per controllarlo dopo
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
            if cb.get() == 1: # 1 significa che è spuntata
                selected_questions.append(cb.cget("text"))

        # 3. Controlla se le domande selezionate sono sufficienti
        if len(selected_questions) < num_requested:
            self.error_label.configure(
                text=f"Error: You requested {num_requested} questions, but selected only {len(selected_questions)}."
            )
            return

        # 4. Estrae casualmente il numero di domande richieste (se ne ha selezionate di più)
        final_questions = random.sample(selected_questions, num_requested)

        # 5. Se è tutto ok, svuota eventuali errori vecchi e avvia l'intervista!
        self.error_label.configure(text="")
        self.controller.show_screen("Screen4", data=final_questions)