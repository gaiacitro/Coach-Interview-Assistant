import os
import customtkinter as ctk

'''CARD_BG = "#FCFDF5"      # Sfondo color panna
CARD_BORDER = "#12BA4B"  # Verde acceso del bordo principale e del titolo
TEXT_GREEN = "#12BA4B"
TEXT_SUB = "#1A5E35"     # Verde un po' più scuro per il sottotitolo
BTN_BG = "#E2F4DF"       # Verde molto chiaro per i bottoni
BTN_TEXT = "#18A542"     # Verde per il testo all'interno dei bottoni
BTN_HOVER = "#CDECCD"    # Colore al passaggio del mouse
'''

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
    print(f"ATTENZIONE: Font non trovato al percorso: {FONT_PATH}")

APP_FONT = "Quicksand"