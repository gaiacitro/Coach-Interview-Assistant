# screens/screen4.py
import random
import webview
import os

class InterviewAPI:
    def __init__(self, questions):
        self.questions = questions.copy()
        random.shuffle(self.questions)

    def get_next_question(self):
        if self.questions:
            q = self.questions.pop(0)
            
            # QUI INSERIREMO LA LOGICA DI SPEECH.PY
            print(f"--- AVVIO REGISTRAZIONE PER: {q} ---")
            
            return q
        else:
            print("--- INTERVISTA FINITA ---")
            return "END"

    def close_window(self):
        if len(webview.windows) > 0:
            webview.windows[0].destroy()

def launch_webview_interview(questions):
        api = InterviewAPI(questions)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_file = os.path.join(current_dir, 'screen4.html')
        
        webview.create_window('Interview In Progress', url=html_file, js_api=api, width=1000, height=700)
        webview.start()