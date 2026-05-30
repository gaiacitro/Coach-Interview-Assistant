# main.py
import customtkinter as ctk

from screens.screen1 import Screen1
from screens.screen2_3 import Screen2_3
from screens.screen5 import Screen5  # <-- IMPORT SCREEN 5

class InterviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Interview Coach Assistant")
        self.geometry("700x800")
        ctk.set_appearance_mode("light")
        
        # Main container where all screens will be rendered
        self.container = ctk.CTkFrame(self, fg_color="white")
        self.container.pack(fill="both", expand=True)
        
        # NOTE: If you want to test Screen 5 directly without doing the interview,
        # simply change "Screen1" to "Screen5" here below!
        self.show_screen("Screen1")

    def clear_container(self):
        # Destroy everything currently inside the container
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
            
        # =======================================================
        # SCHERMATA DI CARICAMENTO & AVVIO INTERVISTA
        # =======================================================
        elif screen_name == "LoadingInterview":
            loading_frame = ctk.CTkFrame(self.container, fg_color="transparent")
            loading_frame.pack(expand=True, fill="both")
            
            ctk.CTkLabel(loading_frame, text="Loading the interview setup...", 
                         font=("Helvetica", 28, "bold"), text_color="black").pack(pady=(250, 10))
            ctk.CTkLabel(loading_frame, text="Initializing AI models. This may take a few seconds", 
                         font=("Helvetica", 16), text_color="gray").pack()
            
            # Disegna la scritta a schermo
            self.update()
            
            # Creiamo una funzione interna che si occupa di far partire l'IA
            def start_interview():
                # 1. QUESTA È LA PARTE PESANTE: Importa l'IA mentre c'è ancora la scritta a schermo
                from screens.screen4 import launch_webview_interview
                
                # 2. ADESSO CHE HA FINITO DI CARICARE, nascondiamo la finestra principale
                self.withdraw()
                self.clear_container()
                
                # 3. Lanciamo il video
                launch_webview_interview(data)
                
                # 4. Quando il video si chiude, riapriamo la finestra e andiamo alla schermata 5
                self.deiconify() 
                self.show_screen("Screen5") 
            
            # Eseguiamo la funzione 100 millisecondi dopo aver mostrato la scritta
            self.after(100, start_interview)
            
        # =======================================================
            
        elif screen_name == "Screen5":
            Screen5(self.container, self, data=data)
            
        else:
            print(f"Error: Screen '{screen_name}' not found.")

if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()