# orchestrator/greeting.py

import sys
import os
import re
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai import STT
from ai import LLM
from ai import TTS


class GreetingOrchestrator:
    """
    Handles the greeting flow with one retry for unclear responses.
    Returns True if user wants to proceed, False otherwise.
    """
    
    def __init__(self, logger = None):
        self.logger = logger
        self.stt = STT(logger=logger)
        self.llm = LLM(logger=logger)
        self.tts = TTS(logger=logger)
        self.max_retries = 1  # Only 1 retry as per requirements
    
    async def execute(self) -> bool:
        """
        Execute greeting flow.
        
        Returns:
            bool: True if user wants to place order, False otherwise
        """
        
        # Step 1: Initial greeting
        greeting = "Assalam o Alaikum, thank you for calling KFC. This is Asad. Kya aap delivery ka order place karna chahtay hain?"
        tts_response = await self.tts.play_audio(greeting)
        print(f"🔊 TTS Response: {tts_response}")
        
        # Try once, with one retry if needed
        for attempt in range(self.max_retries + 1):
            
            # Step 2: Capture user response
            user_response = await self.stt.transcribe()
            print(f"📝 User said: {user_response[::-1]}")
            if self.logger:
                self.logger.info(f"Greeting attempt {attempt + 1} - User said: {user_response}")
            
            # Step 3: Check intent with LLM
            intent = await self._detect_intent(greeting, user_response)
            #print(f"🤖 Intent detected: {intent}")
            if self.logger:
                self.logger.info(f"Greeting attempt {attempt + 1} - Intent detected: {intent}")
            
            # Step 4: Handle based on intent
            if intent == "yes":
                if self.logger:
                    self.logger.info("Greeting - User wants to place order, proceeding")
                # Proceed to next step
                return True
            
            elif intent == "no":
                # User doesn't want to order - transfer to staff
                farewell = "Main aap ko staff se connect kar raha hoon jo aap ki help kar sakta hai. Kindly line per rahein."
                await self.tts.play_audio(farewell)
                if self.logger:
                    self.logger.info("Greeting - User declined order, routing to staff")
                #print("✅ greeting tested successfully")
                return False
            
            else:  # intent == "others"
                # Unclear response
                if attempt < self.max_retries:
                    if self.logger:
                        self.logger.info("Greeting - Intent unclear, retrying greeting")
                    # Play greeting again (only once)
                    greeting_attempt_second  = "Sorry, main aapki baat theek se sun nahi paaya, Kya aap delivery ka order place karna chahtay hain?"
                    tts_second_attempt_response = await self.tts.play_audio(greeting_attempt_second)
                    print(f"🔊 TTS Response: {tts_second_attempt_response}")
                else:
                    # After retry, still unclear - transfer to staff
                    farewell = "Main aap ko staff se connect kar raha hoon jo aap ki help kar sakta hai. Kindly line per rahein."
                    await self.tts.play_audio(farewell)
                    if self.logger:
                        self.logger.info("Greeting - Intent still unclear after retry, routing to staff")
                    #print("✅ greeting tested successfully")
                    return False
        
        return False
    
    async def _detect_intent(self, greeting: str, user_response: str) -> str:
        """
        Hybrid intent detection:
        1. Rule-based keyword matching
        2. LLM fallback if unclear
        
        Returns:
            "yes", "no", or "others"
        """

        if not user_response:
            if self.logger:
                self.logger.warning("Greeting - Empty user response received")
            return "others"
        
        

        # Normalize text
        # text = user_response.lower().strip()
        # text = re.sub(r"[^\w\s]", "", text)

        # -------------------------
        # NO KEYWORDS (CHECK FIRST)
        # -------------------------
        # no_keywords = [
        #     "nahi",
        #     "nahin",
        #     "na",
        #     "abhi nahi",
        #     "order nahi",
        #     "nahi karna",
        #     "cancel",
        #     "galat number",
        #     "wrong number",
        #     "no"
        # ]

        # for word in no_keywords:
        #     if word in text:
        #         if self.logger:
        #             self.logger.info(f"Greeting - Keyword match NO: '{word}' found in: {text}")
        #         return "no"

        # -------------------------
        # YES KEYWORDS
        # -------------------------
        # yes_keywords = [
        #     "ji",
        #     "jee",
        #     "ji haan",
        #     "haan",
        #     "han",
        #     "ha",
        #     "bilkul",
        #     "bilkul theek",
        #     "order karna hai",
        #     "order karna he",
        #     "order likh lein",
        #     "likh lein",
        #     "likh lo",
        #     "haan order",
        #     "jee order",
        #     "karna hai",
        #     "karna he",
        #     "yes"
        # ]

        # for word in yes_keywords:
        #     if word in text:
        #         if self.logger:
        #             self.logger.info(f"Greeting - Keyword match YES: '{word}' found in: {text}")
        #         return "yes"
        

        # -------------------------
        # LLM FALLBACK
        # -------------------------
        if self.logger:
            self.logger.info(f"Greeting - Asking LLM to classify response for: {user_response}")

        prompt = f"""Classify this Urdu response aginst question {greeting}
	as 'yes', 'no' or 'others' to order: "{user_response}" Reply only with: yes, no or others"""

        response = await self.llm.get_response(prompt, temperature=0.0)
        result = response.lower().strip()

        if self.logger:
            self.logger.info(f"Greeting - LLM result: {result}")

        if result == "yes":
            return "yes"
        elif result == "no":
            return "no"
        else:
            return "others"
        

# Test code - run this file directly to test
if __name__ == "__main__":
    import asyncio
    
    async def test_detect_intent():
        """Test the intent detection without running full flow"""
        orchestrator = GreetingOrchestrator()
        greeting = "Assalam o Alaikum, thank you for calling KFC. This is Asad. Kya aap delivery ka order place karna chahtay hain?"
        intent = await orchestrator._detect_intent(greeting, "جی نہیں، مجھے آرڈر نہیں کرنا")
        print(intent)  # Expected: yes
    
    # Run the test
    asyncio.run(test_detect_intent())