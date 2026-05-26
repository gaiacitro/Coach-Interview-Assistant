import customtkinter as ctk

# --- Variabili di Stile (Modificabili centralmente) ---
PRINCIPAL_COLOR = "#ABC07A"
SECONDARY_COLOR = "#C1D397"

class InterviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Interview Coach Assistant")
        self.geometry("700x800")
        ctk.set_appearance_mode("light")
        
        # Container principale per le diverse schermate
        self.container = ctk.CTkFrame(self, fg_color="white")
        self.container.pack(fill="both", expand=True)
        
        # Mostra la prima schermata all'avvio
        self.show_screen_1()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_screen_1(self):
        self.clear_container()
        
        # Padding interno Schermata 1
        main_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=60, pady=60)

        ctk.CTkLabel(main_frame, text="Interview Coach Assistant", 
                     font=("Helvetica", 32, "bold"), text_color="black").pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(main_frame, text="What interview do you want to practice?", 
                     font=("Helvetica", 18), text_color="black").pack(anchor="w", pady=(0, 40))

        # Bottone Job Interview
        self.btn_job = ctk.CTkButton(main_frame, text="   Job interview", font=("Helvetica", 16),
                                     fg_color="#EBEBEB", text_color="black", hover_color=PRINCIPAL_COLOR,
                                     anchor="w", corner_radius=12, height=70, 
                                     command=self.show_screen_2_job)
        self.btn_job.pack(fill="x", pady=12)

        # Bottone University Exam (Ora collegato alla Schermata dell'Esame)
        self.btn_uni = ctk.CTkButton(main_frame, text="   University oral exam", font=("Helvetica", 16),
                                     fg_color="#EBEBEB", text_color="black", hover_color=PRINCIPAL_COLOR,
                                     anchor="w", corner_radius=12, height=70,
                                     command=self.show_screen_2_uni)
        self.btn_uni.pack(fill="x", pady=12)

    def show_screen_2_job(self):
        self.clear_container()
        
        main_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Titolo
        ctk.CTkLabel(main_frame, text="Job Interview Practice", 
                     font=("Helvetica", 28, "bold"), text_color="black").pack(anchor="w", pady=(0, 20))

        # Input numero domande
        ctk.CTkLabel(main_frame, text="Number of questions you want in the interview", 
                     font=("Helvetica", 16, "bold"), text_color="#000000").pack(anchor="w")
        
        self.num_questions = ctk.CTkEntry(main_frame, placeholder_text="e.g. 5", height=45, corner_radius=10)
        self.num_questions.pack(fill="x", pady=(5, 20))

        # Lista domande predefinite
        ctk.CTkLabel(main_frame, text="Select the questions you would like to receive", 
                     font=("Helvetica", 16, "bold"), text_color="#000000").pack(anchor="w", pady=(0, 10))

        # Frame scrollabile per le domande
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", height=300)
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

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
        self.setup_custom_question_section(main_frame)

    def show_screen_2_uni(self):
        self.clear_container()
        
        main_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Titolo specifico per l'università
        ctk.CTkLabel(main_frame, text="University Oral Exam Practice", 
                     font=("Helvetica", 28, "bold"), text_color="black").pack(anchor="w", pady=(0, 20))

        # Input numero domande
        ctk.CTkLabel(main_frame, text="Number of questions you want in the exam", 
                     font=("Helvetica", 16, "bold"), text_color="#000000").pack(anchor="w")
        
        self.num_questions = ctk.CTkEntry(main_frame, placeholder_text="e.g. 3", height=45, corner_radius=10)
        self.num_questions.pack(fill="x", pady=(5, 20))

        # Lista domande (Inizialmente vuota, inserimento manuale)
        ctk.CTkLabel(main_frame, text="Select or add the questions for your exam", 
                     font=("Helvetica", 16, "bold"), text_color="#000000").pack(anchor="w", pady=(0, 10))

        # Frame scrollabile per le domande inserite dall'utente
        self.scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent", height=300)
        self.scroll_frame.pack(fill="both", expand=True, pady=10)

        # Sezione "New custom question" (Fattorizzata per riutilizzarla)
        self.setup_custom_question_section(main_frame)

    def setup_custom_question_section(self, main_frame):
        # Campo di testo + bottone inserimento
        custom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        custom_frame.pack(fill="x", pady=10)

        self.custom_entry = ctk.CTkEntry(custom_frame, placeholder_text="Type a custom question here...", height=40)
        self.custom_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        add_btn = ctk.CTkButton(custom_frame, text="+ Add", width=80, height=40, fg_color=PRINCIPAL_COLOR, 
                                text_color="black", hover_color=SECONDARY_COLOR, command=self.add_custom_question)
        add_btn.pack(side="right")

        # Bottone Invia comune
        submit_btn = ctk.CTkButton(main_frame, text="Invia", font=("Helvetica", 18, "bold"), 
                                   fg_color=PRINCIPAL_COLOR, text_color="black", height=60, corner_radius=15,
                                   hover_color=SECONDARY_COLOR, command=lambda: print("Pratica avviata!"))
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

if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()