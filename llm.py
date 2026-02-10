# llm.py
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()

# Now you can access the variables as if they were set normally
gemini_developer_api_key = os.getenv("GEMINI_DEVELOPER_API_KEY")

# Only run this block for Gemini Developer API
client = genai.Client(api_key=gemini_developer_api_key)

async def process_text(text: str) -> str:
    """
    This method represents LLM validation / processing.
    For PoC: echoes input text.
    Later: replace with GPT / Claude / local LLM.
    """
    return text

def detect_intent_urdu(user_response):
   
    prompt = f"""Classify this Urdu response as 'yes' or 'no':
    "{user_response}"
   
    Reply only with: yes or no"""
 
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=types.Part.from_text(text=prompt),
        config=types.GenerateContentConfig(
            temperature=0,
            top_p=0.95,
            top_k=20,
        ),
    )
 
    result = response.text.strip().lower()
   
    return "yes" if "yes" in result else "no"

def reformat_address_to_english(urdu_address):
   
    prompt = f"""Convert this Urdu text to English address format if it contains an address:
    "{urdu_address}"
   
    Rules:
    - If the text is NOT an address, return: "NOT_AN_ADDRESS"
    - If it is an address:
      • Transcribe EXACTLY what is spoken - do not add or invent words
      • Convert all numbers to English numerals (1, 2, 3...)
      • Replace: مکان/مکان نمبر/باؤس نمبر → House Number or H#
      • Replace: گلی/گلی نمبر → Street Number or Street #
      • Replace: بلاک → Block
      • Keep location names in readable English
      • Output format: House Number [#], [Block Name] Block, [Area], [City]
    
    Output only the reformatted address or "NOT_AN_ADDRESS". Do not add extra words."""
 
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=types.Part.from_text(text=prompt),
        config=types.GenerateContentConfig(
            temperature=0,
            top_p=0.95,
            top_k=20,
        ),
    )
 
    result = response.text.strip()
   
    return result if result != "NOT_AN_ADDRESS" else None