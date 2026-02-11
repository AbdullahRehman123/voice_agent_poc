# orchestrator/address.py

import stt
import llm
import tts


class AddressOrchestrator:
    """
    Handles collecting and validating the delivery address.
    """
    
    async def execute(self, context: dict) -> bool:
        """
        Execute address collection flow.
        
        Args:
            context: Shared context dictionary to store order details
        
        Returns:
            bool: True if successful, False to abort
        """
        
        # Ask for address
        question = "Apna address bataen?"
        await tts.play_audio(question)
        
        # Capture response
        user_response = await stt.transcribe()
        print(f"📝 Address (Urdu): {user_response}")
        
        # Reformat address to English using LLM
        reformatted_address = await self._reformat_address(user_response)
        
        if reformatted_address and reformatted_address != "NOT_AN_ADDRESS":
            # Valid address
            context["address"] = reformatted_address
            print(f"✅ Reformatted Address: {reformatted_address}")
            return True
        else:
            # Invalid address - ask again
            retry_message = "Address ko samajhne mein problem hui. Address doobara bataen."
            await tts.play_audio(retry_message)
            
            # Try one more time
            user_response = await stt.transcribe()
            print(f"📝 Address (retry): {user_response}")
            
            reformatted_address = await self._reformat_address(user_response)
            
            if reformatted_address and reformatted_address != "NOT_AN_ADDRESS":
                context["address"] = reformatted_address
                print(f"✅ Reformatted Address: {reformatted_address}")
                return True
            else:
                # Still invalid - might need to abort or transfer
                print("❌ Could not understand address after retry")
                return False
    
    async def _reformat_address(self, urdu_address: str) -> str:
        """
        Reformat Urdu address to English format using LLM.
        
        Args:
            urdu_address: The address in Urdu
        
        Returns:
            str: Reformatted address in English or "NOT_AN_ADDRESS"
        """
        
        prompt = f"""Convert this Urdu text to English address format if it contains an address:
"{urdu_address}"

Rules:
- If the text is NOT an address, return: "NOT_AN_ADDRESS"
- If it is an address:
  • Transcribe EXACTLY what is spoken - do not add or invent words
  • Convert all numbers to English numerals (1, 2, 3...)
  • Replace: مکان/مکان نمبر/ہاؤس نمبر → House Number or H#
  • Replace: گلی/گلی نمبر → Street Number or Street #
  • Replace: بلاک → Block
  • Keep location names in readable English
  • Output format: House Number [#], [Block Name] Block, [Area], [City]

Output only the reformatted address or "NOT_AN_ADDRESS". Do not add extra words."""
        
        response = await llm.get_response(prompt, temperature=0.0)
        return response.strip()