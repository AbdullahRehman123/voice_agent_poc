# stt.py - Refactored: Only handles speech-to-text transcription

import asyncio
import os
import sounddevice as sd
from speechmatics.rt import AsyncClient, AudioFormat, TranscriptionConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

speechmatics_api_key = os.getenv("SPEECHMATICS_API_KEY")
SAMPLE_RATE = 16000
SILENCE_TIMEOUT = 3.0  # Wait 3 seconds of silence before returning transcription

class STT:
    def __init__(self, logger=None):
        self.api_key = os.getenv("SPEECHMATICS_API_KEY")
        self.sample_rate = 16000
        self.silence_timeout = 3.0
        self.logger = logger # Logger injected from outside

    async def transcribe(self) -> str:
        """
        Single method to capture audio and return transcribed text.
        This is the ONLY public method - all logic stays in orchestrators.
        
        Returns:
            str: The transcribed text from user speech
        """
        
        # Internal state for this transcription session
        accumulated_text = ""
        current_segment = ""
        last_speech_time = None
        silence_confirmed = False
        session_active = True
        
        client = AsyncClient(api_key=speechmatics_api_key)

        if self.logger:
            self.logger.info("STT transcribe() called - starting session")
        
        def on_transcript(msg):
            nonlocal accumulated_text, current_segment, last_speech_time, silence_confirmed
            
            results = msg.get("results", [])
            is_final = any(result.get("is_eos", False) for result in results)
            
            # Build transcript from word results
            full_transcript = ""
            for result in results:
                if result.get("type") == "word":
                    alternatives = result.get("alternatives", [])
                    if alternatives:
                        full_transcript += alternatives[0].get("content", "") + " "
            
            full_transcript = full_transcript.strip()
            
            # Handle partial transcripts
            if not is_final:
                if full_transcript:
                    # Reverse for Urdu display for only printing
                    transcript_display = full_transcript[::-1]
                    accumulated_text = accumulated_text + " " + full_transcript
                    #print(f"⏳ Partial: {transcript_display}")
                    if self.logger:
                        self.logger.debug(f"STT Partial: {accumulated_text}")
                    
                    # Reset silence timer - user is still speaking
                    last_speech_time = None
                    silence_confirmed = False
                return
            
            # Handle final transcript (EOS detected)
            if not full_transcript:
                if self.logger:
                    self.logger.debug("STT EOS received but transcript was empty, skipping")
                return
            
            # Reverse for Urdu display for only printing
            transcript_display = full_transcript[::-1]
            accumulated_text =  accumulated_text + " " + full_transcript
            
            # Add to current segment
            if current_segment:
                current_segment += " " + transcript_display
            else:
                current_segment = transcript_display
            
            #print(f"📜 Received: {transcript_display}")
            if self.logger:
                self.logger.info(f"STT Final segment: {full_transcript}")
                self.logger.debug(f"STT Accumulated so far: {accumulated_text.strip()}")
            
            # Mark when we received final speech
            last_speech_time = asyncio.get_event_loop().time()
            silence_confirmed = False
        
        async def monitor_silence():
            """Monitor for silence timeout to end transcription"""
            nonlocal current_segment, last_speech_time, silence_confirmed, session_active, accumulated_text
            
            while session_active:
                await asyncio.sleep(0.1)
                
                if last_speech_time is not None and not silence_confirmed:
                    current_time = asyncio.get_event_loop().time()
                    time_since_speech = current_time - last_speech_time
                    
                    if time_since_speech >= SILENCE_TIMEOUT:
                        #print(f"\n✅ Silence detected ({SILENCE_TIMEOUT}s) - ending transcription")
                        if self.logger:
                            self.logger.info(f"STT silence detected after {self.silence_timeout}s - ending transcription")
                            self.logger.info(f"STT Returning text: {current_segment}")
                        silence_confirmed = True
                        
                        # Stop the session
                        await client.stop_session()
                        session_active = False
        
        # Register event handlers
        client.on("AddTranscript", on_transcript)
        client.on("RecognitionStarted", lambda msg: print("🎤 Listening..."))
        client.on("Error", lambda msg: print(f"❌ STT Error: {msg}"))
        
        try:
            # Start Speechmatics session
            await client.start_session(
                transcription_config=TranscriptionConfig(
                    language="ur",
                    operating_point="enhanced",
                    enable_partials=True
                ),
                audio_format=AudioFormat(
                    encoding="pcm_s16le",
                    sample_rate=SAMPLE_RATE
                )
            )

            if self.logger:
                self.logger.info("STT Speechmatics session started successfully")

        except Exception as e:
            if self.logger:
                self.logger.error(f"STT failed to start session: {e}")
            raise
        
        # Get event loop
        loop = asyncio.get_event_loop()
        
        # Start silence monitoring
        monitor_task = asyncio.create_task(monitor_silence())
        
        # Audio callback
        def audio_callback(indata, frames, time, status):
            if session_active:
                asyncio.run_coroutine_threadsafe(client.send_audio(indata.tobytes()), loop)
        
        # Start audio stream
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            callback=audio_callback
        )
        
        stream.start()
        if self.logger:
            self.logger.info("STT audio stream started")
        
        try:
            # Wait until session ends
            while session_active:
                await asyncio.sleep(0.1)
        
        except Exception as e:
            if self.logger:
                self.logger.error(f"STT error during session: {e}")
            raise

        finally:
            # Cleanup
            monitor_task.cancel()
            stream.stop()
            stream.close()
            await client.stop_session()
            if self.logger:
                self.logger.info("STT session cleaned up and closed")

        final_text = accumulated_text.strip()

        if self.logger:
            self.logger.info(f"STT transcribe() complete - final result: {final_text}")

        return final_text