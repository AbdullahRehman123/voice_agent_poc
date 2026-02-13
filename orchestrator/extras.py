# orchestrator/extras.py

from ai import STT
from ai import LLM
from ai import TTS


class ExtrasOrchestrator:
    """
    Handles collecting any extras from the user.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.stt = STT(logger=logger)
        self.llm = LLM(logger=logger)
        self.tts = TTS(logger=logger)

    
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
        await self.tts.play_audio(question)

        if self.logger:
            self.logger.info("Extras - Asking user for extras")
        
        # Capture response
        user_response = await self.stt.transcribe()
        print(f"📝 Extras: {user_response[::-1]}")
        if self.logger:
            self.logger.info(f"Extras - User response: {user_response}")
        
        # Store in context
        context["extra"] = user_response
        if self.logger:
            self.logger.info(f"Extras - Stored in context: {user_response}")
        
        return True