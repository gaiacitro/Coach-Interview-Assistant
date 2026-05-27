# screens/screen1_home.py
import customtkinter as ctk
from config import PRINCIPAL_COLOR

class Screen1(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # Inizializza il frame con sfondo trasparente
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.pack(expand=True, fill="both", padx=60, pady=60)

        ctk.CTkLabel(self, text="Interview Coach Assistant", 
                     font=("Helvetica", 32, "bold"), text_color="black").pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self, text="What interview do you want to practice?", 
                     font=("Helvetica", 18), text_color="black").pack(anchor="w", pady=(0, 40))

        # Bottone Job Interview
        self.btn_job = ctk.CTkButton(self, text="   Job interview", font=("Helvetica", 16),
                                     fg_color="#EBEBEB", text_color="black", hover_color=PRINCIPAL_COLOR,
                                     anchor="w", corner_radius=12, height=70, 
                                     command=lambda: self.controller.show_screen("Screen2Job"))
        self.btn_job.pack(fill="x", pady=12)

        # Bottone University Exam
        self.btn_uni = ctk.CTkButton(self, text="   University oral exam", font=("Helvetica", 16),
                                     fg_color="#EBEBEB", text_color="black", hover_color=PRINCIPAL_COLOR,
                                     anchor="w", corner_radius=12, height=70,
                                     command=lambda: self.controller.show_screen("Screen2Uni"))
        self.btn_uni.pack(fill="x", pady=12)