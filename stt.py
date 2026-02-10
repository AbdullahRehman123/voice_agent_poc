# stt.py - SIMPLER FIX: Adjust Speechmatics EOS sensitivity

import asyncio
import os
import sounddevice as sd
from speechmatics.rt import AsyncClient, AudioFormat, TranscriptionConfig
from dotenv import load_dotenv

from functions import (
    case_1_delivery_type,
    case_2_order_item,
    case_3_quantity,
    case_4_extra,
    case_5_address
)

# ======================
# CONFIG
# ======================

# Load environment variables from .env file
load_dotenv()

# Now you can access the variables as if they were set normally
speechmatics_api_key = os.getenv("SPEECHMATICS_API_KEY")
SAMPLE_RATE = 16000
CONFIRMATION_TIMEOUT = 3.0  # Wait 3 seconds after EOS before moving to next case

# ======================
# STATE
# ======================
current_case = 1
context = {}
test = ""

CASE_FUNCTIONS = {
    1: case_1_delivery_type,
    2: case_2_order_item,
    3: case_3_quantity,
    4: case_4_extra,
    5: case_5_address
}

async def transcribe_audio() -> str:
    """
    This method represents STT.
    Returns concatenated transcription after conversation ends.
    FIXED: Waits for confirmation timeout to handle long sentences.
    """
    
    # State management
    accumulated_transcription = ""
    current_case = 1
    context = {}
    session_active = True
    global test
    
    # For handling long sentences
    current_response = ""  # Accumulates text for the current case
    last_eos_time = None   # Track when last EOS was detected
    eos_confirmed = False  # True when we've waited long enough after EOS
    pending_handler = None # Store the handler to execute after confirmation
    
    client = AsyncClient(api_key=speechmatics_api_key)
    
    def on_transcript(msg):
        nonlocal accumulated_transcription, current_case, session_active
        nonlocal current_response, last_eos_time, eos_confirmed, pending_handler
        
        # Check if this is a final transcript
        results = msg.get("results", [])
        is_final = any(result.get("is_eos", False) for result in results)
        global test
        
        # Build the full transcript from all results with type 'word'
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
                transcript_display = full_transcript[::-1]
                test = transcript_display + " " + test
                print(f"⏳ Partial: {transcript_display}")
                
                # If we got more speech after EOS, cancel the pending handler
                if pending_handler is not None:
                    print("   ↪️ More speech detected, continuing to listen...")
                    pending_handler = None
                    last_eos_time = None
                    eos_confirmed = False
            return
        
        # Final transcript detected (EOS)
        if not full_transcript:
            return
        
        transcript_display = full_transcript[::-1]
        test = transcript_display + " " + test
        
        # Add to current response
        if current_response:
            current_response += " " + transcript_display
        else:
            current_response = transcript_display
        
        print(f"\n📜 Received: {transcript_display}")
        #print(f"📝 Current response so far: {current_response[::-1]}")
        
        # Mark that we got an EOS, but don't process immediately
        last_eos_time = asyncio.get_event_loop().time()
        eos_confirmed = False
        
        # Store the handler to execute later (after timeout)
        from functions import CASE_FUNCTIONS
        pending_handler = CASE_FUNCTIONS.get(current_case)
    
    # Background task to monitor EOS confirmation timeout
    async def monitor_eos_confirmation():
        nonlocal current_response, last_eos_time, eos_confirmed, pending_handler
        nonlocal accumulated_transcription, current_case, session_active

        global test
        
        while session_active:
            await asyncio.sleep(0.1)
            
            # Check if we have a pending EOS that needs confirmation
            if last_eos_time is not None and not eos_confirmed:
                current_time = asyncio.get_event_loop().time()
                time_since_eos = current_time - last_eos_time
                
                # If enough time has passed without new speech
                if time_since_eos >= CONFIRMATION_TIMEOUT:
                    print(f"\n✅ Confirmed end of speech after {CONFIRMATION_TIMEOUT}s silence")
                    eos_confirmed = True
                    
                    # Now process the complete response
                    if pending_handler is None:
                        # No handler found - end session
                        await client.stop_session()
                        session_active = False
                        continue
                    
                    # Add to accumulated transcription
                    if accumulated_transcription:
                        accumulated_transcription += " | " + test
                    else:
                        accumulated_transcription = test
                    
                    print(f"📋 Complete user input: {test}")
                    
                    # Call the handler with the COMPLETE response
                    next_case = pending_handler(test, context)
                    
                    # Reset for next input
                    current_response = ""
                    last_eos_time = None
                    pending_handler = None
                    test = ""
                    # Check if conversation is complete
                    if next_case is None or isinstance(next_case, dict):
                        await client.stop_session()
                        session_active = False
                        continue
                    
                    # Move to next case
                    current_case = next_case
    
    # Register event handlers
    client.on("AddTranscript", on_transcript)
    client.on("RecognitionStarted", lambda msg: print("✅ Recognition started!"))
    client.on("Error", lambda msg: print(f"❌ Error: {msg}"))
    client.on("Warning", lambda msg: print(f"⚠️ Warning: {msg}"))
    
    # Start session
    print("🔄 Starting STT Session...")
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
    print("✅ STT Session Started")
    
    # First question
    print("🤖 Assalamualaikum! Kya aap delivery order karna chahte hain?")
    
    # Get event loop
    loop = asyncio.get_event_loop()
    
    # Start the EOS monitoring task
    monitor_task = asyncio.create_task(monitor_eos_confirmation())
    
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
    
    try:
        # Wait until session ends
        while session_active:
            await asyncio.sleep(0.1)
    finally:
        # Cleanup
        monitor_task.cancel()
        stream.stop()
        stream.close()
        await client.stop_session()
        print("✅ STT Session Stopped")
    
    # Return the accumulated transcription
    return accumulated_transcription.strip()