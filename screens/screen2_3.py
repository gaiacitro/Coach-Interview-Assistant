# screens/Screen2_3_interview.py
import customtkinter as ctk
from config import PRINCIPAL_COLOR, SECONDARY_COLOR

class Screen2_3(ctk.CTkFrame):
    def __init__(self, parent, controller, mode="job"):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.pack(expand=True, fill="both", padx=40, pady=40)

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

        # Bottone Invia comune
        # Al posto del vecchio comando lambda, mettiamo:
        submit_btn = ctk.CTkButton(
            self, text="Start the interview", font=("Helvetica", 18, "bold"), 
            fg_color=PRINCIPAL_COLOR, text_color="black", height=60, corner_radius=15,
            hover_color=SECONDARY_COLOR, 
            command=lambda: self.controller.show_screen(
                "Screen4", 
                data=["Domanda di prova 1", "Domanda di prova 2", "Domanda di prova 3"]
            )
        )
        submit_btn.pack(fill="x", pady=(20, 0))

    def add_checkbox(self, text):
        cb = ctk.CTkCheckBox(self.scroll_frame, text=text, font=("Helvetica", 13), 
                             fg_color=PRINCIPAL_COLOR, hover_color=SECONDARY_COLOR, border_color="gray", border_width=2)
        cb.pack(anchor="w", pady=8, padx=10)

    def add_custom_question(self):
        text = self.custom_entry.get()
        if text.strip():
            self.add_checkbox(text)
            self.custom_entry.delete(0, 'end')