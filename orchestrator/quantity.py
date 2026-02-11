# orchestrator/quantity.py

import stt
import llm
import tts


class QuantityOrchestrator:
    """
    Handles collecting the quantity from the user.
    """
    
    async def execute(self, context: dict) -> bool:
        """
        Execute quantity collection flow.
        
        Args:
            context: Shared context dictionary to store order details
        
        Returns:
            bool: True if successful, False to abort
        """
        
        # Ask for quantity
        question = "Quantity bataein"
        await tts.play_audio(question)
        
        # Capture response
        user_response = await stt.transcribe()
        print(f"📝 Quantity: {user_response}")
        
        # Store in context
        context["quantity"] = user_response
        
        return True