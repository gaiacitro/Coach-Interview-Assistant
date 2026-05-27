# main.py
import customtkinter as ctk

from screens.screen1 import Screen1
from screens.screen2_3 import Screen2_3

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

    def show_screen(self, screen_name, data=None):
        self.clear_container()
        
        if screen_name == "Screen1":
            Screen1(self.container, self)
        elif screen_name == "Screen2Job":
            Screen2_3(self.container, self, mode="job")
        elif screen_name == "Screen2Uni":
            Screen2_3(self.container, self, mode="uni")
        elif screen_name == "Screen4":
            self.withdraw() 
            from screens.screen4 import launch_webview_interview
            launch_webview_interview(data)
            self.clear_container()
            self.deiconify() 
            self.show_screen("Screen1") 
            
        else:
            print(f"Errore: Schermata {screen_name} non trovata.")


if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()