# orchestrator/extras.py

import stt
import llm
import tts


class ExtrasOrchestrator:
    """
    Handles collecting any extras from the user.
    """
    
    async def execute(self, context: dict) -> bool:
        """
        Execute extras collection flow.
        
        Args:
            context: Shared context dictionary to store order details
        
        Returns:
            bool: True if successful, False to abort
        """
        
        # Ask for extras
        question = "Kya kuch aur chahiye?"
        await tts.play_audio(question)
        
        # Capture response
        user_response = await stt.transcribe()
        print(f"📝 Extras: {user_response}")
        
        # Store in context
        context["extra"] = user_response
        
        return True