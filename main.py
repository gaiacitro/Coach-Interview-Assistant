# main.py
import customtkinter as ctk
import os
from screens.screen1 import Screen1
from screens.screen2_3 import Screen2_3
from screens.screen5 import Screen5
from config import CARD_BG, APP_FONT, TEXT_MAIN, TEXT_SUB  
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

class InterviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Interview Coach Assistant")

        ctk.set_appearance_mode("light")
        
        self.geometry("1050x800")

        self.configure(fg_color=CARD_BG)

        self.container = ctk.CTkFrame(self, fg_color=CARD_BG)
        self.container.pack(fill="both", expand=True)
        
        self.show_screen("Screen1")

    def clear_container(self):
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
            
        ## Loading screen before the interview
        elif screen_name == "LoadingInterview":
            loading_frame = ctk.CTkFrame(self.container, fg_color=CARD_BG)
            loading_frame.pack(expand=True, fill="both")
            
            ctk.CTkLabel(loading_frame, text="Loading the interview setup...", 
                         font=(APP_FONT, 28, "bold"), text_color=TEXT_MAIN).pack(pady=(250, 10))
            ctk.CTkLabel(loading_frame, text="Initializing AI models. This may take a few seconds", 
                         font=(APP_FONT, 16), text_color=TEXT_SUB).pack()
            
            self.update()
            
            def start_interview():
                from screens.screen4 import launch_webview_interview
                
                self.withdraw()
                self.clear_container()
                
                final_report_data = launch_webview_interview(data)
                
                self.deiconify() 
                self.show_screen("Screen5", data=final_report_data) 
            
            self.after(100, start_interview)
            
        ##
            
        elif screen_name == "Screen5":
            Screen5(self.container, self, data=data)
            
        else:
            print(f"Error: Screen '{screen_name}' not found.")

if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()