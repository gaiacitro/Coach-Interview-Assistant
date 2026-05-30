# screens/screen4.py
import random
import webview
import os
import time
import threading
import sounddevice as sd
from scipy.io.wavfile import write

# Import the specific printing/analyzing function from our backend
from speech import process_and_print_speech_analysis
from hands.mod_detection_hands import HandTrackerGeneral, process_and_print_gesture_analysis # <--- NUOVO IMPORT
from hands.mod_hands_movements import FaceTouchTracker, process_and_print_insecurity_analysis


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
        # Inizializziamo il tracker delle mani
        self.hand_tracker_general = HandTrackerGeneral()
        self.face_touch_tracker = FaceTouchTracker()

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
            print(">>> The avatar is speaking. Recording will start in 3 seconds...")
            
            # Start the 3-second timer
            self.recording_timer = threading.Timer(3.0, self.start_recording)
            self.recording_timer.start()
            
            return q
        else:
            print("\n--- INTERVIEW FINISHED ---")
            return "END"

    # =================================================================
    # VERSION 1: TEST MODE (MOCK RECORDING) - CURRENTLY ACTIVE
    # (Usa i file audio già esistenti per non dover parlare ogni volta)
    # =================================================================
    def start_recording(self):
        print("\n>>> [REC - TEST MODE] Simulation started. Real audio is NOT recorded.")
        self.start_time = time.time()
        self.is_recording = True
        self.hand_tracker_general.start() # <--- AVVIA IL TRACCIAMENTO MANI
        self.face_touch_tracker.start()

    def stop_and_save_recording(self):
        print(">>> [STOP - TEST MODE] Simulation stopped.")

        # Ferma le mani e recupera il tempo speso a gesticolare
        tempo_gesticolazione = self.hand_tracker_general.stop() # <--- FERMA LE MANI
        tempo_tocco_viso = self.face_touch_tracker.stop()

        # Alternates between q1 and q2
        if self.current_q_index % 2 != 0:
            file_path = "response_q1.wav"
        else:
            file_path = "response_q2.wav"
            
        self.is_recording = False
        
        self.session_results.append({
            "question": self.current_question_text,
            "audio_file": file_path,
            "hand_general_time": tempo_gesticolazione, # nuovo
            "face_touch_time": tempo_tocco_viso # <--- Salvi il dato qui
        })
        print(f"    [ Mock audio attached: {file_path} ]")


    # =================================================================
    # VERSION 2: REAL RECORDING MODE - CURRENTLY COMMENTED OUT
    # (Per riattivarla, togli i ''' da qui sotto e mettili attorno alla Version 1)
    # =================================================================
    '''
    def start_recording(self):
        print("\n>>> [REC] Recording started! I am listening.")
        max_duration = 300 
        self.recording_array = sd.rec(int(max_duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
        self.start_time = time.time()
        self.is_recording = True
        
        self.hand_tracker_general.start() # <--- AGGIUNTO ANCHE QUI

    def stop_and_save_recording(self):
        print(">>> [STOP] Recording stopped.")
        sd.stop()
        
        tempo_gesticolazione = self.hand_tracker_general.stop() # <--- AGGIUNTO ANCHE QUI
        
        duration = time.time() - self.start_time
        num_samples = int(duration * self.fs)
        trimmed = self.recording_array[:num_samples]
        file_path = f"response_q{self.current_q_index}.wav"
        write(file_path, self.fs, trimmed)
        
        self.is_recording = False
        
        self.session_results.append({
            "question": self.current_question_text,
            "audio_file": file_path,
            "hand_general_time": tempo_gesticolazione # <--- AGGIUNTO ANCHE QUI
        })
        print(f"    [ Audio saved: {file_path} ]")
    '''

    def run_speech_analysis(self):
        # NUOVO: Salviamo i dati restituiti dal file speech.py in una variabile della classe
        self.final_report_data = process_and_print_speech_analysis(self.session_results)

        print("\nSESSION COMPLETED! The window will close automatically.")
        return "DONE"

    def close_window(self):
        if len(webview.windows) > 0:
            webview.windows[0].destroy()

def launch_webview_interview(questions):
    api = InterviewAPI(questions)
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    html_file = os.path.join(current_dir, 'screen4.html')
    
    webview.create_window('Interview In Progress', url=html_file, js_api=api, width=1000, height=700)
    webview.start()
    
    # NUOVO: Quando webview.start() finisce (la finestra si chiude), restituiamo i dati salvati!
    # Nota: usiamo getattr nel caso l'intervista sia stata chiusa bruscamente prima della fine.
    return getattr(api, 'final_report_data', None)