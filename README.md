# Voice Agent POC

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
│   └── address.py                  # Customer profile fetch + address confirmation
├── integration/                    # External service integrations
│   ├── __init__.py
│   ├── routeToAgent.py             # Route call to human agent
│   └── CustomerProfile.py          # Customer profile lookup + location check
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
- **`integration/`** = External service connections (customer profile, routing, location checks)
- **`logger.py`** = Logging setup, one timestamped file per execution

### 2. Single Responsibility

Each class and method has ONE clear job:

- `STT.transcribe()` → Listens to mic, returns transcribed text
- `LLM.get_response(prompt)` → Sends prompt to Gemini, returns response
- `TTS.play_audio(text)` → Plays audio to caller
- `CustomerProfile.getCustomerProfile(msisdn)` → Fetches customer details
- Each orchestrator → Handles ONE step of the conversation flow

### 3. AI Classes Loaded Once into Memory

All three AI classes are instantiated once in `main.py` and injected into every orchestrator. This means no repeated initialisation on every call.

```python
# main.py - instantiated once per orchestrator
greeting = GreetingOrchestrator(logger=logger)
address = AddressOrchestrator(logger=logger)
# Each orchestrator internally creates: STT(logger), LLM(logger), TTS(logger)
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
  ↓ (Initialize context with msisdn)
  ↓
GreetingOrchestrator
  ├─→ TTS: "Assalam o Alaikum, thank you for calling KFC..."
  ├─→ STT: transcribe()
  ├─→ Intent: keyword match → LLM fallback
  ├─→ yes  → save intent="order" → proceed
  ├─→ no   → RouteToAgent → exit
  └─→ others → retry once → RouteToAgent → exit
       ↓ (if yes)
OrderItemOrchestrator
  ├─→ TTS: "Aap kya order karna chahte hain?"
  └─→ STT: transcribe() → save to context
       ↓
QuantityOrchestrator
  ├─→ TTS: "Quantity bataein"
  └─→ STT: transcribe() → save to context
       ↓
ExtrasOrchestrator
  ├─→ TTS: "Kya kuch aur chahiye?"
  └─→ STT: transcribe() → save to context
       ↓
AddressOrchestrator
  ├─→ CustomerProfile.getCustomerProfile(msisdn)
  │     └─→ returns { customer_name, customer_address, ... }
  │         └─→ saved to context["customer_profile"]
  │
  ├─→ TTS: "Meri baat {name} se ho rahi hai. Aap ka address {address} hai..."
  ├─→ STT: transcribe()
  ├─→ LLM: check address confirmation intent (yes/no/others)
  │
  ├─→ yes   → TTS: "Shukria, Kindly wait karien"
  │           └─→ CustomerProfile.checkAvailableLocation() → exit()
  │
  ├─→ no    → RouteToAgent → exit
  │
  └─→ others → TTS: "Sorry..." + address_question
              ├─→ STT: transcribe()
              ├─→ LLM: check intent again
              ├─→ yes    → TTS: "Shukria..." → checkAvailableLocation() → exit()
              └─→ no/others → RouteToAgent → exit
       ↓
Order Summary printed to terminal
```

---

## 📝 Key Orchestrator Details

### Greeting Orchestrator
Intent detection uses a **hybrid approach**:
1. **Keyword matching first** (fast, no LLM cost)
   - No keywords checked before yes keywords to avoid false positives
2. **LLM fallback** if no keyword matched

Intent outcomes:
- `yes` → Save `context["intent"] = "order"` → Proceed to order flow
- `no` → Play farewell, call `RouteToAgent.routeCallToAgent()`, exit
- `others` → Retry greeting once → if still `others` → same as `no`

### Address Orchestrator
1. **Fetches customer profile** using `context["msisdn"]`
2. **Confirms address** with personalized message using customer name and stored address
3. **Validates response** (yes/no/others) via LLM
4. **On yes**: Says thank you, calls `checkAvailableLocation()`, exits
5. **On no**: Routes to agent
6. **On others**: Retries once with apology, then routes to agent if still unclear

---

## 📊 Context Dictionary

The `context` dictionary stores all data for one call session:

```python
{
    "msisdn": "923001234567",
    "intent": "order",
    "customer_profile": {
        "customerId": 101,
        "customer_name": "John Doe",
        "phone1": "923001234567",
        "customer_address": "G-8, Islamabad"
    },
    "order_item": "Zinger Burger",
    "quantity": "2",
    "extra": "Fries",
    "address": "G-8, Islamabad",
    "cost": None
}
```

---

## 📋 Logging

Every execution creates a new log file in `logs/` with a datetime-stamped filename:

```
logs/
└── 2026-02-13_14-30-00.log
```

**Log file captures:** STT partials, STT finals, LLM prompts, LLM responses, intent decisions, keyword matches, customer profile fetch, errors and warnings.

**Terminal only shows:** the conversation flow — TTS output, user responses, intent results, customer profile fetch, order summary.

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

## 🔧 Extending the System

### Adding a new conversation step:

1. Create `orchestrator/new_step.py`
2. Define class with `__init__(self, logger=None)` and `execute(self, context)` method
3. Instantiate AI services: `self.stt = STT(logger=logger)`, etc.
4. Use `self.stt.transcribe()`, `self.llm.get_response()`, `self.tts.play_audio()`
5. Add to the flow in `main.py`

### Adding a new integration:

1. Create `integration/new_service.py`
2. Define class with required methods
3. Import and instantiate in relevant orchestrator
4. Call methods as needed

---

## 🎯 Sprint Evolution

| Feature | Sprint 1 | Sprint 2 | Sprint 3 |
|---------|----------|----------|----------|
| **AI files** | root directory | `ai/` folder (classes) | ✅ |
| **Intent detection** | LLM only | keyword + LLM fallback | ✅ |
| **Logging** | print only | datetime log files | ✅ |
| **Customer profile** | ❌ | ❌ | ✅ Fetch via msisdn |
| **Address flow** | Simple LLM reformat | Simple LLM reformat | ✅ Profile-based confirmation |
| **Routing** | ❌ | stub | ✅ Called on no/others |
| **Context** | order details only | order details only | ✅ Full session (msisdn, profile, intent) |
| **Startup delay** | ❌ | 1 second | ✅ |

---

## 📞 Integration Points

### CustomerProfile Service

**`getCustomerProfile(msisdn)`**
- Input: Phone number string
- Output: Dict with `customerId`, `customer_name`, `phone1`, `customer_address`
- Currently returns static data — replace with real API call

**`checkAvailableLocation(customer_address)`**
- Input: Address string
- Output: None (exits for now)
- Currently stub — implement delivery zone validation

### RouteToAgent Service

**`routeCallToAgent(context_str)`**
- Input: Full context as string
- Output: None
- Currently stub — implement call transfer logic

---

## 🔍 Debugging

Check the log file in `logs/` for detailed execution trace including:
- STT partial and final transcriptions
- LLM prompts and responses
- Customer profile API calls
- Intent detection results
- Routing decisions

Terminal output is kept clean showing only the conversation flow.
