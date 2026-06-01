# screens/screen1_home.py
import customtkinter as ctk
from config import (
    CARD_BG, 
    CARD_BORDER, 
    TEXT_GREEN,
    TEXT_SUB,
    BTN_BG, 
    BTN_TEXT, 
    BTN_HOVER,
    APP_FONT  # <-- Importiamo la costante del font
)

class Screen1(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, 
                         fg_color=CARD_BG, 
                         border_color=CARD_BORDER, 
                         border_width=5, 
                         corner_radius=20)
        self.controller = controller

        self.pack(expand=True, padx=40, pady=40, ipadx=60, ipady=40)

        # Creiamo gli oggetti font usando la costante APP_FONT importata da config
        font_titolo = ctk.CTkFont(family=APP_FONT, size=32, weight="bold")
        font_sottotitolo = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")
        font_bottoni = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")

        # Titolo
        ctk.CTkLabel(self, text="Interview Coach Assistant", 
                     font=font_titolo, text_color=TEXT_GREEN).pack(pady=(40, 10), anchor="center")

        # Sottotitolo
        ctk.CTkLabel(self, text="What interview do you want to practice?", 
                     font=font_sottotitolo, text_color=TEXT_SUB).pack(pady=(0, 40), anchor="center")

        # Bottone Job
        self.btn_job = ctk.CTkButton(self, text="Job interview", font=font_bottoni,
                                     fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER,
                                     corner_radius=12, height=60, 
                                     command=lambda: self.controller.show_screen("Screen2Job"))
        self.btn_job.pack(fill="x", padx=60, pady=10)

        # Bottone Uni
        self.btn_uni = ctk.CTkButton(self, text="University oral exam", font=font_bottoni,
                                     fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER,
                                     corner_radius=12, height=60,
                                     command=lambda: self.controller.show_screen("Screen2Uni"))
        self.btn_uni.pack(fill="x", padx=60, pady=10)



