# KFC Voice Agent

## 📁 Project Structure

```
voice_agent_poc/
├── main.py                         # Entry point - orchestrates the flow
├── logger.py                       # Rotating datetime-based logger setup
├── ai/                             # AI service classes (loaded into memory once)
│   ├── __init__.py
│   ├── stt.py                      # Speech-to-Text class (Speechmatics)
│   ├── llm.py                      # LLM class (Google Gemini)
│   └── tts.py                      # Text-to-Speech class
├── orchestrator/                   # Business logic - one file per conversation step
│   ├── __init__.py
│   ├── greeting.py                 # Greeting + intent detection (yes/no/others, 1 retry)
│   ├── order_item.py               # Order item collection
│   ├── quantity.py                 # Quantity collection
│   ├── extras.py                   # Extras collection
│   └── address.py                  # Address collection + LLM reformatting
├── integration/                    # External service integrations
│   ├── __init__.py
│   └── routeToAgent.py             # Route call to human agent (stub)
├── logs/                           # Auto-created, one log file per execution
│   └── 2026-02-13_14-30-00.log
├── .env                            # API keys (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture Principles

### 1. Separation of Concerns

- **`ai/`** = Technical implementations only (how to transcribe, how to call LLM, how to speak)
- **`orchestrator/`** = Business logic only (what to ask, when, retry logic, decisions)
- **`integration/`** = External service connections (routing, CRM, etc.)
- **`logger.py`** = Logging setup, one timestamped file per execution

### 2. Single Responsibility

Each class and method has ONE clear job:

- `STT.transcribe()` → Listens to mic, returns transcribed text
- `LLM.get_response(prompt)` → Sends prompt to Gemini, returns response
- `TTS.play_audio(text)` → Plays audio to caller
- Each orchestrator → Handles ONE step of the conversation flow

### 3. AI Classes Loaded Once into Memory

All three AI classes are instantiated once in `main.py` and injected into every orchestrator. This means no repeated initialisation on every call.

```python
# main.py - instantiated once
stt = STT(logger=logger)
llm = LLM(logger=logger)
tts = TTS(logger=logger)

# Injected into each orchestrator
greeting = GreetingOrchestrator(logger=logger)  # internally uses same pattern
```

### 4. Easy to Swap AI Services

Want to switch from Speechmatics to Google STT? Only change `ai/stt.py` — keep `transcribe()` signature the same.
Want to switch from Gemini to GPT-4 or Claude? Only change `ai/llm.py` — keep `get_response(prompt)` signature the same.

Orchestrators never need to change when switching providers.

---

## 🎯 Conversation Flow

```
main.py
  ↓ (1 second delay)
GreetingOrchestrator
  ├─→ TTS: "Assalam o Alaikum, thank you for calling KFC..."
  ├─→ STT: transcribe()
  ├─→ Intent: keyword match → LLM fallback
  ├─→ yes  → proceed
  ├─→ no   → RouteToAgent → exit
  └─→ others → retry once → RouteToAgent → exit
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
  ├─→ LLM: reformat Urdu address to English
  └─→ Invalid → retry once → abort
       ↓
Order Summary printed to terminal
```

---

## 📝 Greeting Orchestrator Details

Intent detection uses a **hybrid approach**:

1. **Keyword matching first** (fast, no LLM cost)
   - No keywords checked before yes keywords to avoid false positives
2. **LLM fallback** if no keyword matched

Intent outcomes:
- `yes` → Proceed to order flow
- `no` → Play farewell, call `RouteToAgent.routeCallToAgent()`, exit
- `others` → Retry greeting once → if still `others` → same as `no`

---

## 📋 Logging

Every execution creates a new log file in `logs/` with a datetime-stamped filename:

```
logs/
└── 2026-02-13_14-30-00.log
```

**Log file captures:** STT partials, STT finals, LLM prompts, LLM responses, intent decisions, keyword matches, errors and warnings.

**Terminal only shows:** the conversation flow — TTS output, user responses, intent results, order summary.

---

## 🚀 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment — create a `.env` file:**
   ```
   SPEECHMATICS_API_KEY=your_key_here
   GEMINI_DEVELOPER_API_KEY=your_key_here
   ```

3. **Run the agent:**
   ```bash
   python main.py
   ```

---

## 📊 Context Dictionary

The `context` dictionary is built up across orchestrators and contains the full order at the end:

```python
{
    "order_item": "Zinger Burger",
    "quantity": "2",
    "extra": "Fries",
    "address": "House Number 5, B Block, DHA Phase 2, Lahore"
}
```

---

## 🔧 Extending the System

### Adding a new conversation step:

1. Create `orchestrator/new_step.py`
2. Define class with `__init__(self, logger=None)` and `execute(self, context)` method
3. Use `self.stt.transcribe()`, `self.llm.get_response()`, `self.tts.play_audio()`
4. Add to the flow in `main.py`

### Adding a new integration:

1. Create `integration/new_service.py`
2. Define class with required methods
3. Import and call from relevant orchestrator

---

## 🎯 Key Improvements from Sprint 1 → Sprint 2

| | Sprint 1 | Sprint 2 |
|---|---|---|
| AI files location | root directory | `ai/` folder |
| AI services | standalone functions | classes loaded into memory |
| Intent detection | LLM only | keyword match + LLM fallback |
| Logging | print statements only | rotating datetime log files |
| Human handoff | not implemented | `integration/routeToAgent.py` stub |
| Startup delay | none | 1 second delay in `main.py` |