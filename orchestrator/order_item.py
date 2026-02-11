# orchestrator/order_item.py

import stt
import llm
import tts


class OrderItemOrchestrator:
    """
    Handles collecting the order item from the user.
    """
    
    async def execute(self, context: dict) -> bool:
        """
        Execute order item collection flow.
        
        Args:
            context: Shared context dictionary to store order details
        
        Returns:
            bool: True if successful, False to abort
        """
        
        # Ask what they want to order
        question = "Aap kya order karna chahte hain?"
        await tts.play_audio(question)
        
        # Capture response
        user_response = await stt.transcribe()
        print(f"📝 User wants to order: {user_response}")
        
        # Store in context
        context["order_item"] = user_response
        
        return True