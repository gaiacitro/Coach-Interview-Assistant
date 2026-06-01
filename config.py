import os
import customtkinter as ctk

# config.py
PRINCIPAL_COLOR = "#ABC07A"
SECONDARY_COLOR = "#C1D397"


CARD_BG = "#FCFDF5"      # Sfondo color panna
CARD_BORDER = "#12BA4B"  # Verde acceso del bordo principale e del titolo
TEXT_GREEN = "#12BA4B"
TEXT_SUB = "#1A5E35"     # Verde un po' più scuro per il sottotitolo
BTN_BG = "#E2F4DF"       # Verde molto chiaro per i bottoni
BTN_TEXT = "#18A542"     # Verde per il testo all'interno dei bottoni
BTN_HOVER = "#CDECCD"    # Colore al passaggio del mouse

# --- SETUP DEL FONT ---
# Trova il percorso assoluto della cartella dove si trova questo file config.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Costruisci il percorso corretto: entra nella cartella "font" e prende il file
FONT_PATH = os.path.join(BASE_DIR, "font", "Quicksand-VariableFont_wght.ttf") # <-- INSERISCI IL NOME ESATTO DEL FILE

# Carica il font globalmente
if os.path.exists(FONT_PATH):
    ctk.FontManager.load_font(FONT_PATH)
else:
    print(f"ATTENZIONE: Font non trovato al percorso: {FONT_PATH}")

# Salva il nome della famiglia in una costante da esportare
APP_FONT = "Quicksand"