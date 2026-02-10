# main.py
import asyncio
import stt
import llm
import tts

async def voice_agent_controller():
    print("IVR started")
    
    # 1️⃣ Pause before greeting
    print("Waiting 2 seconds before greeting...")
    await asyncio.sleep(2)
    
    greeting_text = "Hello, welcome to our service. How may I help you?"
    
    # 2️⃣ Play greeting (TTS)
    greeting_response = await tts.play_audio(greeting_text)
    print(f"TTS played greeting: {greeting_response}")
    
    # 3️⃣ Listen and transcribe (STT)
    print("Listening for user response...")
    
    user_text_reversed = await stt.transcribe_audio()
    #user_text_reversed = user_text[::-1] #  Reverse the text for display for urdu language
    print(f"STT completed with text: {user_text_reversed}")
    
    # 4️⃣ Process with LLM
    #print("Sending text to LLM...")
    #llm_result = await llm.process_text(user_text_reversed)
    #print(f"LLM returned: {llm_result}")
    
    # 5️⃣ Play response via TTS
    #print("Playing response via TTS...")
    #final_output = await tts.play_audio(llm_result)
    #print(f"TTS played response: {final_output}")
    
    print("IVR flow completed")

if __name__ == "__main__":
    asyncio.run(voice_agent_controller())