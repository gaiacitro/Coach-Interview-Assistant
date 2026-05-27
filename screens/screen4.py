# screens/screen4.py
import customtkinter as ctk
import cv2
from PIL import Image
import random

class Screen4(ctk.CTkFrame):
    # Nota che ora accettiamo un parametro in più: 'selected_questions'
    def __init__(self, parent, controller, selected_questions):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Salviamo e mischiamo le domande scelte dall'utente
        self.questions = selected_questions.copy()
        random.shuffle(self.questions)
        self.current_question = ""

        # --- Impostazioni Video (Sostituisci col tuo percorso) ---
        self.video_path = "assets/loop.mp4" 
        self.cap = cv2.VideoCapture(self.video_path)

        # --- Elementi dell'Interfaccia ---
        # Label che mostrerà la domanda
        self.question_label = ctk.CTkLabel(
            self, 
            text="Premi SPAZIO per mostrare la prima domanda e iniziare...", 
            font=("Helvetica", 24, "bold"), 
            text_color="black",
            wraplength=600 # Se la domanda è lunga, va a capo
        )
        self.question_label.pack(pady=(30, 20))

        # Schermo per il video
        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(expand=True, fill="both")

        # Istruzioni in basso
        self.info_label = ctk.CTkLabel(
            self, 
            text="Premi [SPAZIO] quando hai finito di rispondere per passare alla prossima", 
            font=("Helvetica", 14), 
            text_color="gray"
        )
        self.info_label.pack(pady=20)

        # --- Binding della Tastiera ---
        # Diciamo alla finestra principale di ascoltare la barra spaziatrice
        self.controller.bind("<space>", self.next_question)

        # Avvia il loop del video
        self.update_frame()

    def update_frame(self):
        # Legge il fotogramma e gestisce il loop
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            # Puoi aggiustare la grandezza del video qui (es. 800x450)
            ctk_image = ctk.CTkImage(light_image=pil_image, size=(640, 360)) 
            self.video_label.configure(image=ctk_image)

        self._loop_id = self.after(30, self.update_frame)

    def next_question(self, event=None):
        # Se ci sono ancora domande nella lista
        if self.questions:
            # Estrae la prima domanda dalla lista mischiata
            self.current_question = self.questions.pop(0)
            self.question_label.configure(text=self.current_question)
            
            # QUI (nel prossimo step) INSERIREMO LA LOGICA DI SPEECH.PY
            print(f"--- AVVIO REGISTRAZIONE PER: {self.current_question} ---")
            
        else:
            # Se le domande sono finite
            self.question_label.configure(text="Intervista terminata! Calcolo dei risultati...")
            self.info_label.configure(text="")
            
            # Smettiamo di ascoltare la barra spaziatrice
            self.controller.unbind("<space>") 
            
            print("--- INTERVISTA FINITA ---")
            # Dopo 2 secondi, andiamo alla schermata 5 (per ora chiudiamo)
            self.after(2000, self.stop_and_go_back)

    def stop_and_go_back(self):
        # Ferma il loop video
        if hasattr(self, '_loop_id'):
            self.after_cancel(self._loop_id)
        self.cap.release()
        
        # Per ora torniamo alla home. Poi lo manderemo alla schermata 5
        self.controller.show_screen("Screen1Home")