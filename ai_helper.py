# ai_helper.py
import os
from dotenv import load_dotenv
from google import genai # <--- La NUOVA libreria

# Carica i segreti dal file .env
load_dotenv()

# Prende la chiave in modo sicuro
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# Configura il client secondo le nuove direttive di Google
client = genai.Client(api_key=GEMINI_API_KEY)

def get_reformulated_text(original_text):
    """
    Invia il testo a Gemini e restituisce la frase pulita da filler words ed errori.
    Restituisce None se c'è un errore di connessione.
    """
    try:
        prompt = f"""
        You are an expert interview coach. Rewrite the following sentence spoken by a candidate during an interview. 
        Your goal is to fix grammatical errors, remove stutters, and eliminate filler words (like 'um', 'uh', 'basically', 'like', 'so'). 
        CRITICAL RULES:
        - Do NOT change the original meaning.
        - Do NOT add new concepts or exaggerate.
        - Keep the vocabulary simple and the tone as close to the original as possible.
        - Only output the corrected sentence, nothing else.

        Candidate's original text: "{original_text}"
        """
        
        # Facciamo la richiesta usando il nuovissimo modello gemini-2.5-flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"[ERRORE AI] Problema con Gemini: {e}")
        return None