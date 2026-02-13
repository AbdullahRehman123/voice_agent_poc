# ai/llm.py

from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

gemini_developer_api_key = os.getenv("GEMINI_DEVELOPER_API_KEY")
client = genai.Client(api_key=gemini_developer_api_key)

class LLM:

    def __init__(self, logger=None):
        self.api_key = os.getenv("GEMINI_DEVELOPER_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.logger = logger

    async def get_response(self, prompt: str, temperature: float = 0.0) -> str:
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
            if self.logger:
                self.logger.info(f"LLM Prompt: {prompt}")

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=types.Part.from_text(text=prompt),
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=0.95,
                    top_k=20,
                ),
            )
            result = response.text.strip()

            if self.logger:
                self.logger.info(f"LLM Response: {result}")
            
            return result
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"LLM Error: {e}")
            return ""