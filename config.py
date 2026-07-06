import os
import customtkinter as ctk

CARD_BG = "#FDF7EE"      
CARD_BORDER = "#8CA19B"  
TEXT_MAIN = "#8C5F3B"    
TEXT_SUB = "#4A3B32"     

BTN_BG = "#F4EBD7"       
BTN_TEXT = "#8C5F3B"     
BTN_HOVER = "#E6DABC"    

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "font", "Quicksand-VariableFont_wght.ttf") # <-- INSERISCI IL NOME ESATTO DEL FILE

if os.path.exists(FONT_PATH):
    ctk.FontManager.load_font(FONT_PATH)
else:
    print(f"ATTENTION: Font not found at path: {FONT_PATH}")

APP_FONT = "Quicksand"