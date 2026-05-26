import collections
import os
import time
import random
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

# To avoid Windows problems with symlinks in Hugging Face cache
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.silence import detect_silence

# --- DATABASE OF QUESTIONS ---
QUESTION_DB = [
    "Tell me about yourself.",
    "What are your greatest strengths?",
    "What is your greatest weakness?",
    "Why do you want to work for this company?",
    "Where do you see yourself in five years?",
    "How do you handle pressure or stressful situations?",
    "Describe a difficult work situation and how you overcame it.",
    "Why should we hire you?"
]

# Model loading (loaded once at startup)
print("Loading AI model... please wait...")
model = WhisperModel("base.en", device="cpu", compute_type="int8")

def record_audio(filename, current_question, fs=44100):
    """Records audio for a specific question and trims it exactly"""
    print(f"\n" + "-"*50)
    print(f"QUESTION: {current_question}")
    print("-"*50)
    input("Press ENTER to start your answer...")
    
    # Start timer and recording # 2]
    start_time = time.time()
    max_duration = 300 # 5 minutes buffer # 2]
    recording = sd.rec(int(max_duration * fs), samplerate=fs, channels=1, dtype='int16') # 2]
    
    print(">>> Recording... Press ENTER to STOP recording.")
    input() 
    
    # Stop and trim # 3]
    sd.stop()
    duration_seconds = time.time() - start_time
    num_samples = int(duration_seconds * fs)
    trimmed_recording = recording[:num_samples] # 3]
    
    write(filename, fs, trimmed_recording) 
    return filename

def analyze_response(audio_path):
    """Analyzes a specific audio file for silences and filler words"""
    audio = AudioSegment.from_file(audio_path)
    silences = detect_silence(audio, min_silence_len=500, silence_thresh=-45)
    
    # Transcription with VAD # 4]
    segments, _ = model.transcribe(
        audio_path, 
        beam_size=5, 
        initial_prompt="Uhm, er, ah, so, like, well, basically...", # 4]
        word_timestamps=True,
        vad_filter=True, # 4]
        vad_parameters=dict(min_silence_duration_ms=500) # 4]
    )
    
    full_text = " ".join([segment.text for segment in segments]).lower()
    
    # Cleaning # 5]
    for p in [".", ",", "!", "?", "-"]:
        full_text = full_text.replace(p, " ")
    words = full_text.split()
    
    # Counting # 6]
    filler_words_target = ["so", "basically", "actually", "literally", "like", "mean", "well"]
    vocal_fillers_target = ["uhm", "um", "uh", "ah", "er", "mm", "mhh", "erm"]
    
    word_counts = collections.Counter(words) # 6]
    
    return {
        "text": full_text,
        "silence_count": len(silences),
        "filler_found": {w: word_counts[w] for w in filler_words_target if word_counts[w] > 0},
        "vocal_fillers_found": {m: word_counts[m] for m in vocal_fillers_target if word_counts[m] > 0}
    }

# --- MAIN SESSION ---
if __name__ == "__main__":
    print("\n=== WELCOME TO YOUR AI INTERVIEW COACH ===")
    
    # Ask user for number of questions
    try:
        total_q = int(input(f"How many questions would you like to practice? (Max {len(QUESTION_DB)}): "))
        total_q = min(total_q, len(QUESTION_DB))
    except ValueError:
        total_q = 3
        print("Invalid input. Defaulting to 3 questions.")

    # Select random unique questions
    selected_questions = random.sample(QUESTION_DB, total_q)
    
    session_results = []

    # Interview Loop
    for idx, question in enumerate(selected_questions):
        file_path = f"response_q{idx}.wav"
        
        # 1. Record
        record_audio(file_path, question)
        
        # 2. Analyze after 
        # Better to analyze after recording to keep the user "in the zone"
        session_results.append({
            "question": question,
            "audio_file": file_path
        })

    # Final Processing and Report
    print("\n" + "="*50)
    print("ANALYZING YOUR ENTIRE INTERVIEW... PLEASE WAIT")
    print("="*50)

    for result in session_results:
        # Perform analysis on each saved file # 7]
        analysis = analyze_response(result["audio_file"])
        
        print(f"\nQUESTION: {result['question']}")
        print(f"YOUR ANSWER: \"{analysis['text'].strip()}\"") # 7]
        
        # Metrics # 8]
        v_count = sum(analysis['vocal_fillers_found'].values())
        f_count = sum(analysis['filler_found'].values())
        
        print(f"  > Long Pauses: {analysis['silence_count']}")
        print(f"  > Vocal Fillers (uhm, er...): {v_count} {analysis['vocal_fillers_found']}") # 8]
        print(f"  > Filler Words (like, so...): {f_count} {analysis['filler_found']}") # 8]
        print("-" * 30)

    print("\nSESSION COMPLETE. GOOD LUCK WITH YOUR PREPARATION!")