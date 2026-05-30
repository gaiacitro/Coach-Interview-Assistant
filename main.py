# main.py
import customtkinter as ctk

from screens.screen1 import Screen1
from screens.screen2_3 import Screen2_3
from screens.screen5 import Screen5  # <-- IMPORT SCREEN 5

class InterviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Interview Coach Assistant")

        ctk.set_appearance_mode("light")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # 2. Forza le dimensioni della finestra partendo dall'angolo alto a sinistra (+0+0)
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 3. Usa un ritardo microscopico per applicare lo 'zoomed' solo DOPO la creazione
        self.after(0, lambda: self.state('zoomed'))
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
                from screens.screen4 import launch_webview_interview
                
                self.withdraw()
                self.clear_container()
                
                # MODIFICA: Catturiamo il pacchetto dati in uscita dall'intervista!
                final_report_data = launch_webview_interview(data)
                
                # Riapriamo la finestra
                self.deiconify() 
                
                # MODIFICA: Passiamo i dati veri alla Schermata 5!
                self.show_screen("Screen5", data=final_report_data) 
            
            self.after(100, start_interview)
            
        # =======================================================
            
        elif screen_name == "Screen5":
            Screen5(self.container, self, data=data)
            
        else:
            print(f"Error: Screen '{screen_name}' not found.")

if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()