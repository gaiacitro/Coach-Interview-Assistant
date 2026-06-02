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
    
    # 1. Calcoliamo la durata totale dell'audio in secondi
    audio_duration_sec = len(audio) / 1000.0
    
    # 2. Rileviamo TUTTI i silenzi superiori a 250ms
    all_silences = detect_silence(audio, min_silence_len=250, silence_thresh=-45)
    
    long_pauses_count = 0
    micro_silences_count = 0
    
    # 3. Dividiamo i silenzi in due categorie calcolando la loro durata
    for start, end in all_silences:
        duration = end - start
        if duration >= 4000:
            long_pauses_count += 1
        else:
            micro_silences_count += 1
            
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
        "duration_seconds": audio_duration_sec,
        "silence_count": long_pauses_count,            # Pause di panico (>= 4s)
        "micro_silences_count": micro_silences_count,  # Frammentazione (250ms - 3999ms)
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
    
    final_data = [] 
    
    for result in session_results:
        audio_path = result["audio_file"]
        question = result["question"]
        
        try:
            analysis = analyze_speech(audio_path)
            
            v_count = sum(analysis['vocal_fillers_found'].values())
            f_count = sum(analysis['filler_found'].values())
            
            tremor_percent = analysis['voice_tremor_percent']
            tremor_100 = min(100, int((tremor_percent / 3.0) * 100))
            
            print(f"\nQUESTION: {question}")
            print(f"YOUR ANSWER: \"{analysis['text'].strip()}\"")
            print(f"  > Audio Duration: {analysis['duration_seconds']:.1f}s")
            print(f"  > Long Pauses: {analysis['silence_count']}")
            print(f"  > Micro Silences: {analysis['micro_silences_count']}")
            print(f"  > Vocal Fillers: {v_count} {analysis['vocal_fillers_found']}")
            print(f"  > Filler Words: {f_count} {analysis['filler_found']}")
            print(f"  > Voice Tremor: {tremor_100}/100")
            
            if tremor_100 < 33:
                print("      [Feedback: Very steady and confident voice]")
            elif 33 <= tremor_100 <= 66:
                print("      [Feedback: Slight instability, natural for an interview]")
            else:
                print("      [Feedback: High tremor detected (Tense or nervous voice)]")
                
            print("-" * 30)
            
            # --- LA MAGIA: Arricchiamo il dizionario "result" esistente ---
            result["text"] = analysis['text'].strip()
            result["audio_duration"] = analysis['duration_seconds']
            result["silence_count"] = analysis['silence_count']
            result["micro_silences"] = analysis['micro_silences_count']
            result["vocal_fillers"] = v_count
            result["vocal_fillers_dict"] = analysis['vocal_fillers_found']
            result["filler_words"] = f_count
            result["filler_words_dict"] = analysis['filler_found']
            result["tremor"] = tremor_100
            
            final_data.append(result)
            
        except Exception as e:
            print(f"Error during analysis of file {audio_path}: {e}")
            
            # Arricchiamo con valori a 0 in caso di errore
            result["text"] = "[Error: Audio transcription failed]"
            result["audio_duration"] = 0.0
            result["silence_count"] = 0
            result["micro_silences"] = 0
            result["vocal_fillers"] = 0
            result["vocal_fillers_dict"] = {}
            result["filler_words"] = 0
            result["filler_words_dict"] = {}
            result["tremor"] = 0
            
            final_data.append(result)

    return final_data