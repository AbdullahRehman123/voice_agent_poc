# orchestrator/quantity.py

from ai import STT
from ai import LLM
from ai import TTS


class QuantityOrchestrator:
    """
    Handles collecting the quantity from the user.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.stt = STT(logger=logger)
        self.llm = LLM(logger=logger)
        self.tts = TTS(logger=logger)
    
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
        await self.tts.play_audio(question)

        if self.logger:
            self.logger.info("Quantity - Asking user for quantity")
        
        # Capture response
        user_response = await self.stt.transcribe()
        #print(f"📝 Quantity: {user_response}")
        if self.logger:
            self.logger.info(f"Quantity - User response: {user_response}")
        
        # Store in context
        context["quantity"] = user_response
        if self.logger:
            self.logger.info(f"Quantity - Stored in context: {user_response}")
        
        return True