# UAE Visa & Government Intelligence AI Voice Agent

An intelligent, voice-powered AI assistant that allows anyone to ask questions about **UAE Visas, Emirates ID, Overstay Fines, Work Permits, and Government Laws** in natural speech (English, Arabic, Hindi, Urdu, etc.) and receive instant, verified answers spoken back in human voice.

---

## Setup & Working Instructions

### Prerequisites
- Python 3.10 or higher

### 1. Installation
```bash
git clone https://github.com/Shaaha-7/uae-visa-agent.git
cd uae-visa-agent
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the repo root with the following keys:
```env
CONTEXT_DEV_API_KEY=your_context_dev_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
GROQ_API_KEY=your_groq_api_key
```

### 3. Run
Start the live webhook server:
```bash
python server.py
```
The server starts on `http://localhost:5000` (expose port 5000 via ngrok or Cloudflare Tunnels for ElevenLabs webhook integration).

Other entry points:
- `python main.py` — one-shot CLI demo (asks a hardcoded question, prints the answer, optionally generates audio)
- `python voice_agent_pipeline.py` — full local voice loop: microphone → STT → extraction → LLM summary → TTS playback
- `python test_llm.py` — smoke-tests the LLM summarizer against a few sample questions

---

## Architecture Overview

```
[ User / ElevenLabs Voice Agent ]
            │ (Webhook POST /api/visa-intel)
            ▼
     [ Flask Webhook Server ] (server.py)
            │
            ▼
  [ Smart Router & Client ] (gov_intel/uae_visa_client.py)
   ├── 1. Disk Cache Lookup (visa_cache.json) -> Instant verification
   └── 2. Live Extractor (context.dev API) -> Scraping official u.ae/icp portals
            │
            ▼
 [ Groq LLM Voice Summarizer ] (gov_intel/llm_summarizer.py)
   ├── 1. Language Detector (Llama-3.3 70B)
   └── 2. Conversational Speech Script Generator
            │
            ▼
[ ElevenLabs Multilingual TTS ] -> Speaks back to user in their native language
```

Full component breakdown, API schemas, and design rationale: [TECH_SPEC.md](TECH_SPEC.md)

---

## What It Does

1. **Voice-in / Voice-out multilingual interface**: listens to user questions in English, Arabic, Hindi, Urdu, or French, and responds aloud in the user's native language using ElevenLabs TTS.
2. **Verified live UAE government data**: queries official government portals (`u.ae`, `icp.gov.ae`, `gdrfad.gov.ae`) via `context.dev` web extraction, avoiding hallucinated visa rules, eligibility thresholds, and fee structures.
3. **Resilient fallback cache**: maintains a pre-compiled persistent disk cache (`visa_cache.json`) covering 21+ major UAE government categories (Golden Visa, overstay fines, Emirates ID, family sponsorship, labour law, etc.) so the demo keeps working even if API credits run out.

---

## Author

**Shabeer Ahamed K**
