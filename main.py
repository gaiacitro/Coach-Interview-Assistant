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
            
        elif screen_name == "Screen4":
            self.withdraw() # Hides the main menu while interview runs
            
            from screens.screen4 import launch_webview_interview
            launch_webview_interview(data)
            
            self.clear_container()
            self.deiconify() # Shows the menu again
            
            # CHANGED: Now it goes to Screen 5 (Report) instead of Screen 1!
            self.show_screen("Screen5") 
            
        elif screen_name == "Screen5":
            # Renders the final report screen
            Screen5(self.container, self, data=data)
            
        else:
            print(f"Error: Screen '{screen_name}' not found.")

if __name__ == "__main__":
    app = InterviewApp()
    app.mainloop()