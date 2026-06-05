import customtkinter as ctk
from config import (
    CARD_BG, 
    CARD_BORDER, 
    TEXT_MAIN,
    TEXT_SUB,
    BTN_BG, 
    BTN_TEXT, 
    BTN_HOVER,
    APP_FONT  
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

        
        title_font = ctk.CTkFont(family=APP_FONT, size=32, weight="bold")
        subtitle_font = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")
        buttons_font = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")

        # title
        ctk.CTkLabel(self, text="Interview Coach Assistant", 
                     font=title_font, text_color=TEXT_MAIN).pack(pady=(40, 10), anchor="center")

        # subtitle
        ctk.CTkLabel(self, text="What interview do you want to practice?", 
                     font=subtitle_font, text_color=TEXT_SUB).pack(pady=(0, 40), anchor="center")

        # Job button
        self.btn_job = ctk.CTkButton(self, text="Job interview", font=buttons_font,
                                     fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER,
                                     corner_radius=12, height=60, 
                                     command=lambda: self.controller.show_screen("Screen2Job"))
        self.btn_job.pack(fill="x", padx=60, pady=10)

        # University button
        self.btn_uni = ctk.CTkButton(self, text="University oral exam", font=buttons_font,
                                     fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER,
                                     corner_radius=12, height=60,
                                     command=lambda: self.controller.show_screen("Screen2Uni"))
        self.btn_uni.pack(fill="x", padx=60, pady=10)



