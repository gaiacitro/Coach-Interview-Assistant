# main.py
import customtkinter as ctk

# --- MODIFICA QUI: Importa le classi dai nuovi nomi dei file ---
from screens.screen1 import Screen1
from screens.screen2 import Screen2

class InterviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Interview Coach Assistant")
        self.geometry("700x800")
        ctk.set_appearance_mode("light")
        
        # Container principale dove verranno inserite le schermate
        self.container = ctk.CTkFrame(self, fg_color="white")
        self.container.pack(fill="both", expand=True)
        
        # Inizia mostrando la prima schermata
        self.show_screen("Screen1")

    def clear_container(self):
        # Distrugge tutto ciò che è attualmente dentro il contenitore
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_screen(self, screen_name):
        self.clear_container()
        
        # Inizializza la classe corretta in base al nome richiesto
        if screen_name == "Screen1":
            Screen1(self.container, self)
            
        elif screen_name == "Screen2Job":
            Screen2(self.container, self, mode="job")
            
        elif screen_name == "Screen2Uni":
            Screen2(self.container, self, mode="uni")
            
        else:
            print(f"Errore: Schermata {screen_name} non trovata.")

if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()