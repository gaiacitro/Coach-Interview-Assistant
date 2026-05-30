# speech.py
import os
import collections
import parselmouth
from parselmouth.praat import call
from faster_whisper import WhisperModel
from pydub import AudioSegment
from pydub.silence import detect_silence

# Avoid Windows problems with Hugging Face symlinks
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

print("[BACKEND] Loading Whisper AI model... please wait...")
model = WhisperModel("base.en", device="cpu", compute_type="int8")
print("[BACKEND] Voice model ready!")

def analyze_voice_tremor(audio_path):
    """Calculates the Jitter (tremor) level of the audio"""
    try:
        sound = parselmouth.Sound(audio_path)
        pointProcess = call(sound, "To PointProcess (periodic, cc)", 75, 500)
        jitter = call(pointProcess, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        return jitter * 100 
    except Exception as e:
        print(f"Jitter Error: {e}")
        return 0.0

def analyze_speech(audio_path):
    """Core function to extract data from a single audio file."""
    audio = AudioSegment.from_file(audio_path)
    silences = detect_silence(audio, min_silence_len=500, silence_thresh=-45)
    
    tremor_score = analyze_voice_tremor(audio_path)
    
    segments, _ = model.transcribe(
        audio_path, 
        beam_size=5, 
        initial_prompt="Uhm, er, ah, so, like, well, basically...", 
        word_timestamps=True,
        vad_filter=True, 
        vad_parameters=dict(min_silence_duration_ms=500) 
    )
    full_text = " ".join([segment.text for segment in segments]).lower()
    
    for p in [".", ",", "!", "?", "-"]:
        full_text = full_text.replace(p, " ")
    words = full_text.split()
    
    filler_words_target = ["so", "basically", "actually", "literally", "like", "mean", "well"]
    vocal_fillers_target = ["uhm", "um", "uh", "ah", "er", "mm", "mhh", "erm"]
    word_counts = collections.Counter(words) 
    
    return {
        "text": full_text,
        "silence_count": len(silences),
        "filler_found": {w: word_counts[w] for w in filler_words_target if word_counts[w] > 0},
        "vocal_fillers_found": {m: word_counts[m] for m in vocal_fillers_target if word_counts[m] > 0},
        "voice_tremor_percent": tremor_score
    }

def process_and_print_speech_analysis(session_results):
    """
    Takes the list of session results, runs the AI analysis, 
    prints formatted output to the console AND returns the data.
    """
    print("\n" + "="*50)
    print("SPEECH ANALYSIS IN PROGRESS... PLEASE WAIT")
    print("="*50)
    
    # NUOVO: Lista per raccogliere i dati da inviare alla Schermata 5
    final_data = [] 
    
    for result in session_results:
        audio_path = result["audio_file"]
        question = result["question"]
        
        try:
            analysis = analyze_speech(audio_path)
            
            v_count = sum(analysis['vocal_fillers_found'].values())
            f_count = sum(analysis['filler_found'].values())
            tremor = analysis['voice_tremor_percent']
            
            print(f"\nQUESTION: {question}")
            print(f"YOUR ANSWER: \"{analysis['text'].strip()}\"")
            print(f"  > Long Pauses: {analysis['silence_count']}")
            print(f"  > Vocal Fillers: {v_count} {analysis['vocal_fillers_found']}")
            print(f"  > Filler Words: {f_count} {analysis['filler_found']}")
            print(f"  > Voice Tremor (Jitter): {tremor:.2f}%")
            
            if tremor < 1.0:
                print("      [Feedback: Very steady and confident voice]")
            elif 1.0 <= tremor <= 2.0:
                print("      [Feedback: Slight instability, natural for an interview]")
            else:
                print("      [Feedback: High tremor detected (Tense or nervous voice)]")
                
            print("-" * 30)
            
            # --- MODIFICA: AGGIUNTI I DIZIONARI DELLE PAROLE ---
            final_data.append({
                "question": question,
                "text": analysis['text'].strip(),
                "silence_count": analysis['silence_count'],
                "vocal_fillers": v_count,
                "vocal_fillers_dict": analysis['vocal_fillers_found'], # <-- NUOVO
                "filler_words": f_count,
                "filler_words_dict": analysis['filler_found'],         # <-- NUOVO
                "tremor": tremor
            })
            
        except Exception as e:
            print(f"Error during analysis of file {audio_path}: {e}")
            # --- MODIFICA: AGGIUNTI I DIZIONARI VUOTI IN CASO DI ERRORE ---
            final_data.append({
                "question": question,
                "text": "[Error: Audio transcription failed]",
                "silence_count": 0, 
                "vocal_fillers": 0, "vocal_fillers_dict": {},
                "filler_words": 0, "filler_words_dict": {},
                "tremor": 0.0
            })

    # NUOVO: Restituiamo il pacchetto completo!
    return final_data