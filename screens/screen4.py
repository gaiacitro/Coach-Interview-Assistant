# screens/screen4.py
import random
import webview
import os
import time
import threading
import sounddevice as sd
from scipy.io.wavfile import write

# Import delle funzioni di backend
from speech import process_and_print_speech_analysis
from union_face_hands import UnifiedVisionTracker, process_and_print_vision_report # <--- NUOVO IMPORT UNIFICATO


class InterviewAPI:
    def __init__(self, questions):
        self.questions = questions.copy()
        random.shuffle(self.questions)
        
        self.is_recording = False
        self.start_time = 0
        self.recording_array = None
        self.fs = 44100
        self.current_q_index = 0
        self.recording_timer = None 
        
        self.session_results = []
        self.current_question_text = ""
        
        # Inizializziamo l'unico tracker visivo integrato
        self.vision_tracker = UnifiedVisionTracker() # <--- ATTIVAZIONE UNICA

    def get_next_question(self):
        # Cancel any pending 3-second timer if user presses space early
        if self.recording_timer is not None:
            self.recording_timer.cancel()

        # Stop and save the previous recording
        if self.is_recording:
            self.stop_and_save_recording()

        if self.questions:
            q = self.questions.pop(0)
            self.current_question_text = q
            self.current_q_index += 1
            
            print(f"\n--- QUESTION {self.current_q_index}: {q} ---")
            print(">>> The avatar is speaking. Calibration in progress for 3 seconds...")
            
            # MODIFICATO: Avvia la calibrazione SUBITO mentre l'avatar legge la domanda
            self.vision_tracker.start()
            
            # Start the 3-second timer per iniziare la registrazione audio
            self.recording_timer = threading.Timer(3.0, self.start_recording)
            self.recording_timer.start()
            
            return q
        else:
            print("\n--- INTERVIEW FINISHED ---")
            return "END"

    # =================================================================
    # VERSION 1: TEST MODE (MOCK RECORDING) - CURRENTLY ACTIVE
    # =================================================================
    def start_recording(self):
        print("\n>>> [REC - TEST MODE] Audio recording started. Vision tracking + calibration already active.")
        self.start_time = time.time()
        self.is_recording = True
        # MODIFICATO: Vision tracker è già avviato in get_next_question() durante la calibrazione
        # Qui facciamo solo marcare l'inizio dell'audio

    def stop_and_save_recording(self):
        print(">>> [STOP] Recording stopped. Calibration complete. Collecting CV data...")

        # Riceviamo il dizionario già impacchettato dal backend visivo
        # La calibrazione è stata completata durante i 3 secondi di attesa
        cv_data_dict = self.vision_tracker.stop()

        if self.current_q_index % 2 != 0:
            file_path = "response_q1.wav"
        else:
            file_path = "response_q2.wav"
            
        self.is_recording = False
        
        # Salviamo audio, domanda e i dati CV strutturati
        self.session_results.append({
            "question": self.current_question_text,
            "audio_file": file_path,
            "cv_data": cv_data_dict  # <-- Inserito in modo pulitissimo
        })
        print(f"    [ Mock audio attached: {file_path} ]")
    # =================================================================
    # VERSION 2: REAL RECORDING MODE - CURRENTLY COMMENTED OUT
    # =================================================================
    '''
    def start_recording(self):
        print("\n>>> [REC] Audio recording started. Vision tracking + calibration already active.")
        max_duration = 300 
        self.recording_array = sd.rec(int(max_duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
        self.start_time = time.time()
        self.is_recording = True
        
        # MODIFICATO: Vision tracker è già avviato in get_next_question() durante la calibrazione 

    def stop_and_save_recording(self):
        print(">>> [STOP] Recording stopped. Calibration complete. Collecting CV data...")
        sd.stop()
        
        # Riceviamo il dizionario già impacchettato dal backend visivo!
        # La calibrazione è stata completata durante i 3 secondi di attesa
        cv_data_dict = self.vision_tracker.stop()
        
        duration = time.time() - self.start_time
        num_samples = int(duration * self.fs)
        trimmed = self.recording_array[:num_samples]
        file_path = f"response_q{self.current_q_index}.wav"
        write(file_path, self.fs, trimmed)
        
        self.is_recording = False
        
        # Salviamo audio, domanda e i dati CV strutturati
        self.session_results.append({
            "question": self.current_question_text,
            "audio_file": file_path,
            "cv_data": cv_data_dict  # <--- Inserito qui in modo pulito
        })
        print(f"    [ Audio saved: {file_path} ]")
    '''

    def run_speech_analysis(self):
        # 1. Avvia l'analisi vocale di pydub e Whisper
        self.final_report_data = process_and_print_speech_analysis(self.session_results)
        
        # 2. Avvia il report visivo integrato a schermo
        process_and_print_vision_report(self.session_results) # <--- NUOVA CHIAMATA REPORT

        print("\nSESSION COMPLETED! The window will close automatically.")
        return "DONE"

    def close_window(self):
        if len(webview.windows) > 0:
            webview.windows[0].destroy()


def launch_webview_interview(questions):
    api = InterviewAPI(questions)
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    html_file = os.path.join(current_dir, 'screen4.html')
    
    # MODIFICA QUI: Mettiamo larghezza e altezza grandissime per sicurezza + maximized=True
    webview.create_window(
        'Interview In Progress', 
        url=html_file, 
        js_api=api, 
        width=1920, 
        height=1080,
        maximized=True
    )
    
    webview.start()
    
    # NUOVO: Quando webview.start() finisce (la finestra si chiude), restituiamo i dati salvati!
    # Nota: usiamo getattr nel caso l'intervista sia stata chiusa bruscamente prima della fine.
    return getattr(api, 'final_report_data', None)