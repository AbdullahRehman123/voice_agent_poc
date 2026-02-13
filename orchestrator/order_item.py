# orchestrator/order_item.py

from ai import STT
from ai import LLM
from ai import TTS


class OrderItemOrchestrator:
    """
    Handles collecting the order item from the user.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.stt = STT(logger=logger)
        self.llm = LLM(logger=logger)
        self.tts = TTS(logger=logger)
    
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
        await self.tts.play_audio(question)

        if self.logger:
            self.logger.info("OrderItem - Asking user for order item")
        
        # Capture response
        user_response = await self.stt.transcribe()
        #print(f"📝 User wants to order: {user_response}")

        if self.logger:
            self.logger.info(f"OrderItem - User response: {user_response}")
        
        # Store in context
        context["order_item"] = user_response
        if self.logger:
            self.logger.info(f"OrderItem - Stored in context: {user_response}")
        
        return True