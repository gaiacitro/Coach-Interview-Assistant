# ai_helper.py
import os
from dotenv import load_dotenv
from google import genai 

# load environment variables from .env file
load_dotenv()

# get the Gemini API key in a secure way from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
client = genai.Client(api_key=GEMINI_API_KEY)

def get_reformulated_text(original_text):
    """
    Send the text to Gemini, and it returns the sentence with filler words and errors removed.
    Returns None if there is a connection error.
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
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"[ERROR AI] Problem with Gemini: {e}")
        return None