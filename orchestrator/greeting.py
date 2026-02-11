# orchestrator/greeting.py

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stt
import llm
import tts


class GreetingOrchestrator:
    """
    Handles the greeting flow with one retry for unclear responses.
    Returns True if user wants to proceed, False otherwise.
    """
    
    def __init__(self):
        self.max_retries = 1  # Only 1 retry as per requirements
    
    async def execute(self) -> bool:
        """
        Execute greeting flow.
        
        Returns:
            bool: True if user wants to place order, False otherwise
        """
        
        # Step 1: Initial greeting
        greeting = "Assalam o Alaikum, thank you for calling KFC. This is Asad. Kya aap delivery ka order place karna chahtay hain?"
        tts_response = await tts.play_audio(greeting)
        print(f"🔊 TTS Response: {tts_response}")
        
        # Try once, with one retry if needed
        for attempt in range(self.max_retries + 1):
            
            # Step 2: Capture user response
            user_response = await stt.transcribe()
            print(f"📝 User said: {user_response}")
            
            # Step 3: Check intent with LLM
            intent = await self._detect_intent(user_response)
            print(f"🤖 Intent detected: {intent}")
            
            # Step 4: Handle based on intent
            if intent == "yes":
                # Proceed to next step
                return True
            
            elif intent == "no":
                # User doesn't want to order - transfer to staff
                farewell = "Main aap ko staff se connect kar raha hoon jo aap ki help kar sakta hai. Kindly line per rahein."
                await tts.play_audio(farewell)
                print("✅ greeting tested successfully")
                return False
            
            else:  # intent == "others"
                # Unclear response
                if attempt < self.max_retries:
                    # Ask again (only once)
                    retry_message = "Sorry me apki bat nahi samajha, Kya aap delivery ka order place karna chahtay hain?"
                    await tts.play_audio(retry_message)
                else:
                    # After retry, still unclear - transfer to staff
                    farewell = "Main aap ko staff se connect kar raha hoon jo aap ki help kar sakta hai. Kindly line per rahein."
                    await tts.play_audio(farewell)
                    print("✅ greeting tested successfully")
                    return False
        
        return False
    
    async def _detect_intent(self, user_response: str) -> str:
        """
        Detect user intent using LLM.
        
        Args:
            user_response: The user's spoken text
        
        Returns:
            str: "yes", "no", or "others"
        """
        
        prompt = f"""Classify this Urdu response as 'yes' or 'no': "{user_response}" Reply only with: yes or no"""
        
        response = await llm.get_response(prompt, temperature=0.0)
        result = response.lower().strip()
        
        # Ensure we return a valid intent
        if "yes" in result:
            return "yes"
        elif "no" in result:
            return "no"
        else:
            return "others"
        

# Test code - run this file directly to test
if __name__ == "__main__":
    import asyncio
    
    async def test_detect_intent():
        """Test the intent detection without running full flow"""
        orchestrator = GreetingOrchestrator()
        
        intent = await orchestrator._detect_intent("جی بالکل")
        print(intent)  # Expected: yes
    
    # Run the test
    asyncio.run(test_detect_intent())