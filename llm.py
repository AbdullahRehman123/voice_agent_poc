# llm.py - Refactored: Only handles LLM communication

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

gemini_developer_api_key = os.getenv("GEMINI_DEVELOPER_API_KEY")
client = genai.Client(api_key=gemini_developer_api_key)


async def get_response(prompt: str, temperature: float = 0.0) -> str:
    """
    Single method to get LLM response for any prompt.
    This is the ONLY public method - all prompt engineering stays in orchestrators.
    
    Args:
        prompt: The prompt to send to the LLM
        temperature: Temperature setting for response randomness (default: 0 for deterministic)
    
    Returns:
        str: The LLM's response text
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=types.Part.from_text(text=prompt),
            config=types.GenerateContentConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=20,
            ),
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return ""