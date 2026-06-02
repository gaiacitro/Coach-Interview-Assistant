# screens/screen4.py
import random
import webview
import os
import time
import threading
import sounddevice as sd
from scipy.io.wavfile import write
from speech import process_and_print_speech_analysis
from union_face_hands import UnifiedVisionTracker


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
        
        self.vision_tracker = UnifiedVisionTracker() 

    def get_next_question(self):
        if self.recording_timer is not None:
            self.recording_timer.cancel()

        # stop and save the previous recording
        if self.is_recording:
            self.stop_and_save_recording()

        if self.questions:
            q = self.questions.pop(0)
            self.current_question_text = q
            self.current_q_index += 1

            self.vision_tracker.start()
            # the recording will start after 3 seconds, giving time for the vision tracker to calibrate and collect baseline data
            self.recording_timer = threading.Timer(3.0, self.start_recording)
            self.recording_timer.start()
            
            return q
        else:
            return "END"

    # =================================================================
    # VERSION 1: TEST MODE (MOCK RECORDING) 
    # =================================================================
    def start_recording(self):
        print("\n>>> [REC - TEST MODE] Audio recording started. Vision tracking + calibration already active.")
        self.start_time = time.time()
        self.is_recording = True

    def stop_and_save_recording(self):
        cv_data_dict = self.vision_tracker.stop()

        if self.current_q_index % 2 != 0:
            file_path = "response_q1.wav"
        else:
            file_path = "response_q2.wav"
            
        self.is_recording = False

        self.session_results.append({
            "question": self.current_question_text,
            "audio_file": file_path,
            "cv_data": cv_data_dict  
        })
    # =================================================================
    # VERSION 2: REAL RECORDING MODE 
    # =================================================================
    '''
    def start_recording(self):
        print("\n>>> [REC] Audio recording started. Vision tracking + calibration already active.")
        max_duration = 300 
        self.recording_array = sd.rec(int(max_duration * self.fs), samplerate=self.fs, channels=1, dtype='int16')
        self.start_time = time.time()
        self.is_recording = True

    def stop_and_save_recording(self):
        print(">>> [STOP] Recording stopped. Calibration complete. Collecting CV data...")
        sd.stop()
 
        cv_data_dict = self.vision_tracker.stop()

        duration = time.time() - self.start_time
        num_samples = int(duration * self.fs)
        trimmed = self.recording_array[:num_samples]
        file_path = f"response_q{self.current_q_index}.wav"
        write(file_path, self.fs, trimmed)
        
        self.is_recording = False

        self.session_results.append({
            "question": self.current_question_text,
            "audio_file": file_path,
            "cv_data": cv_data_dict  # <--- Inserito qui in modo pulito
        })
        print(f"    [ Audio saved: {file_path} ]")
    '''

    def run_speech_analysis(self):
        # start speech analysis for each recorded answer and save the reformulated text in the session results
        self.final_report_data = process_and_print_speech_analysis(self.session_results)
        
        return "DONE"

    def close_window(self):
        if len(webview.windows) > 0:
            webview.windows[0].destroy()


def launch_webview_interview(questions):
    api = InterviewAPI(questions)
    
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    html_file = os.path.join(current_dir, 'screen4.html')

    webview.create_window(
        'Interview In Progress', 
        url=html_file, 
        js_api=api, 
        width=1920, 
        height=1080,
        maximized=True
    )
    
    webview.start()
    return getattr(api, 'final_report_data', None)