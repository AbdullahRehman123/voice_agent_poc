# KFC Voice Agent - Refactored Architecture

## 📁 Project Structure

```
voice_agent_refactored/
├── main.py                      # Entry point - orchestrates the flow
├── stt.py                       # Speech-to-Text (simple interface)
├── llm.py                       # LLM interface (simple interface)
├── tts.py                       # Text-to-Speech (simple interface)
├── orchestrator/                # Business logic folder
│   ├── __init__.py
│   ├── greeting.py             # Handles greeting + intent detection
│   ├── order_item.py           # Handles order item collection
│   ├── quantity.py             # Handles quantity collection
│   ├── extras.py               # Handles extras collection
│   └── address.py              # Handles address collection + validation
├── requirements.txt
├── .env.example
└── README.md
```

## 🏗️ Architecture Principles

### 1. Separation of Concerns

- **Orchestrators** = Business logic (what to ask, when, retry logic)
- **STT** = Technical implementation (only transcribes)
- **LLM** = Technical implementation (only returns AI response)
- **TTS** = Technical implementation (only speaks text)

### 2. Single Responsibility

Each module has ONE clear job:

- `stt.py` → `transcribe()` - Returns transcribed text
- `llm.py` → `get_response(prompt)` - Returns LLM response
- `tts.py` → `play_audio(text)` - Plays audio
- Each orchestrator → Handles ONE step of the conversation

### 3. Easy to Swap Services

Want to change from Speechmatics to Google STT? Just modify `stt.py`.
Want to change from Gemini to GPT-4? Just modify `llm.py`.

The orchestrators don't need to change!

## 🎯 Flow Diagram

```
main.py
  ↓
GreetingOrchestrator
  ├─→ TTS: "Assalam o Alaikum..."
  ├─→ STT: transcribe()
  ├─→ LLM: detect_intent()
  └─→ Decision: yes/no/others (1 retry)
       ↓ (if yes)
OrderItemOrchestrator
  ├─→ TTS: "Aap kya order karna chahte hain?"
  └─→ STT: transcribe()
       ↓
QuantityOrchestrator
  ├─→ TTS: "Quantity bataein"
  └─→ STT: transcribe()
       ↓
ExtrasOrchestrator
  ├─→ TTS: "Kya kuch aur chahiye?"
  └─→ STT: transcribe()
       ↓
AddressOrchestrator
  ├─→ TTS: "Apna address bataen?"
  ├─→ STT: transcribe()
  ├─→ LLM: reformat_address()
  └─→ Validation (1 retry)
       ↓
Order Summary
```

## 🚀 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Run the agent:**
   ```bash
   python main.py
   ```

## 📝 Greeting Orchestrator Details

### Flow:
1. Play greeting
2. Capture user response
3. Detect intent (yes/no/others)
4. If "others" → Ask again (1 retry only)
5. If still "others" → Transfer to staff
6. If "no" → Transfer to staff
7. If "yes" → Proceed to next step

### Success Message:
When greeting completes (yes/no/transfer), prints: `"✅ greeting tested successfully"`

## 🔧 Extending the System

### Adding a new orchestrator:

1. Create `orchestrator/new_step.py`
2. Implement `execute(context)` method
3. Use `stt.transcribe()`, `llm.get_response()`, `tts.play_audio()`
4. Add to `main.py` flow

### Changing STT service:

Just modify `stt.py` → keep the `transcribe()` signature the same.

### Changing LLM service:

Just modify `llm.py` → keep the `get_response(prompt)` signature the same.

## 🎤 Testing Individual Components

```python
# Test STT only
import asyncio
import stt

async def test_stt():
    text = await stt.transcribe()
    print(f"Transcribed: {text}")

asyncio.run(test_stt())
```

```python
# Test LLM only
import asyncio
import llm

async def test_llm():
    response = await llm.get_response("What is 2+2?")
    print(f"LLM Response: {response}")

asyncio.run(test_llm())
```

## 📊 Context Dictionary

The `context` dictionary is shared across all orchestrators:

```python
{
    "order_item": "Zinger Burger",
    "quantity": "2",
    "extra": "Fries",
    "address": "House Number 123, B Block, DHA, Lahore"
}
```

## 🎯 Key Improvements from Original Code

1. ✅ **Clear separation** - Each file has ONE job
2. ✅ **Easy to test** - Each component can be tested independently
3. ✅ **Easy to swap** - Change STT/LLM service without touching orchestrators
4. ✅ **Follows requirements** - Greeting has exactly 1 retry, as specified
5. ✅ **Maintainable** - New developers can understand the flow easily
6. ✅ **Scalable** - Easy to add new conversation steps

## 📞 Support

For questions, contact the development team.