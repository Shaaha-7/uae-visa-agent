# Technical Specification & System Architecture

This document covers the problem, architecture, component breakdown, API schemas, and design decisions for the **UAE Visa & Government Intelligence AI Voice Agent**.

---

## Problem

Navigating UAE immigration laws, visa eligibility, Emirates ID rules, and overstay fine structures is notoriously complex. Expats, tourists, employers, and elderly residents face fragmented government portals, legal jargon, and language barriers (especially non-English/non-Arabic speakers).

**Why voice?** Immigration queries are urgent and personal — users often want quick answers while traveling or multitasking. A voice interface lowers the accessibility barrier for non-tech-savvy users and supports natural, multilingual spoken conversation in their native language (Hindi, Urdu, Arabic, English, etc.).

---

## System Architecture

The system consists of four layers:

```
[ ElevenLabs Conversational AI Agent / User Voice Input ]
             │ (Webhook HTTP POST)
             ▼
      [ Flask Webhook Server ] (server.py)
             │
             ▼
  [ Smart Router & Client ] (gov_intel/uae_visa_client.py)
      ├── 1. Disk Cache Lookup (visa_cache.json)
      └── 2. Live Extractor (context.dev API) -> Official UAE Portals (u.ae, icp.gov.ae)
             │ (Extracted JSON)
             ▼
  [ LLM Voice Summarizer ] (gov_intel/llm_summarizer.py)
      ├── 1. Groq Language Detection (Llama 3.3 70B)
      └── 2. Multilingual Speech Synthesizer
             │ (Spoken Response Text)
             ▼
[ ElevenLabs Voice Response / Audio Output ]
```

---

## Component Breakdown

### 1. Webhook Server (`server.py`)
- **Framework**: Flask
- **Endpoint**: `POST /api/visa-intel`
- **Port**: 5000 (exposed via ngrok / Cloudflare Tunnels)
- **Role**: Normalizes incoming payloads from ElevenLabs Conversational AI Agents, extracts parameter keys (`question`, `query`, `input`), routes requests to `UAEVisaIntelClient` + `LLMVoiceSummarizer`, and formats multi-key JSON responses (`response`, `result`, `answer`, `output`) to satisfy ElevenLabs agent response parsing.

### 2. UAE Government Intelligence Client (`gov_intel/uae_visa_client.py`)
- **Source constraints**: strict URL binding to official domains (`u.ae`, `icp.gov.ae`, `gdrfad.gov.ae`, `mofa.gov.ae`).
- **Dynamic extractor (`smart_extract`)**: uses natural language keyword matching to select the optimal target URL and builds schema payloads for `context.dev` (`/v1/web/extract`).
- **Caching**: persistent JSON file storage (`visa_cache.json`). If `context.dev` API credits are exhausted or a timeout occurs, the client falls back to cached records to maintain uptime.

### 3. LLM Voice Summarizer (`gov_intel/llm_summarizer.py`)
- **Primary model**: Groq `llama-3.3-70b-versatile` (fallback: OpenAI `gpt-4o-mini` / rule-based template).
- **Language detection**: identifies the language (English, Arabic, Hindi, Urdu, etc.) via a low-token Groq call, and answers in that same language.
- **System prompt design**: forces natural, warm, 2–3 sentence spoken output (60–80 words max), stripped of markdown/bullet formatting for speech engines.

### 4. Voice Speaker Engine (`gov_intel/voice_speaker.py`)
- **STT**: ElevenLabs Scribe v2
- **TTS**: ElevenLabs `eleven_multilingual_v2`
- **Audio capture**: `sounddevice` + `scipy` for the local microphone pipeline (`voice_agent_pipeline.py`)

---

## Data Schemas & API Contracts

### `POST /api/visa-intel` request (ElevenLabs webhook)
```json
{
  "question": "What are the requirements for the UAE Golden Visa for real estate investors?"
}
```

### Server response
```json
{
  "response": "To qualify for the 5-year Golden Visa as a real estate investor, you must own property in the UAE worth at least 2 million dirhams without mortgage loans. You can apply directly through the ICP Smart Services portal or GDRFA Dubai.",
  "result": "...",
  "answer": "...",
  "output": "..."
}
```

### context.dev extraction request (`POST /v1/web/extract`)
```json
{
  "url": "https://u.ae/en/information-and-services/visa-and-emirates-id/Types-of-visas/golden-visa",
  "instructions": "Extract eligibility criteria, financial thresholds, documents required, and validity period for real estate investors.",
  "schema": {
    "type": "object",
    "properties": {
      "topic": { "type": "string" },
      "direct_answer": { "type": "string" },
      "eligibility_criteria": {
        "type": "array",
        "items": { "type": "string" }
      },
      "fees_or_validity": { "type": "string" }
    },
    "required": ["topic", "direct_answer"]
  }
}
```

---

## Tool Rationale

- **ElevenLabs**: state-of-the-art multilingual TTS (`eleven_multilingual_v2`), Scribe v2 STT, and real-time webhook tool integration with low latency.
- **context.dev**: chosen because generic search APIs return unstructured blog posts or agency ads. context.dev does schema-driven extraction directly from official government portals, avoiding hallucinated legal facts.
- **Groq (`llama-3.3-70b-versatile`)**: near-instant inference (~200ms) for language detection and response synthesis, keeping voice turn-taking under 1.5 seconds.

---

## Environment Variables

| Key | Description | Required |
|---|---|---|
| `CONTEXT_DEV_API_KEY` | Bearer token for the context.dev web extraction API | Yes |
| `ELEVENLABS_API_KEY` | API key for ElevenLabs TTS / STT and voice agent | Yes |
| `ELEVENLABS_VOICE_ID` | Default voice ID for TTS synthesis | Yes |
| `GROQ_API_KEY` | API key for the Groq Llama-3.3-70B multilingual LLM | Yes |
| `OPENAI_API_KEY` | Optional fallback LLM key | No |

---

## Security & Best Practices

- **Secret protection**: `.env` is listed in `.gitignore` to prevent credential leakage.
- **Input sanitization**: normalizes terminal encoding (`sys.stdout`) to prevent cp1252 character-map crashes on non-ASCII scripts (Arabic, Devanagari).
- **HTTPS transport**: HTTPS tunnels (ngrok / Cloudflare) are required since ElevenLabs webhooks enforce HTTPS strictly.

---

## Build Approach

Built as a modular system within a 6-hour hackathon window:
1. **Modular architecture** — web extraction (`uae_visa_client.py`), LLM summarization (`llm_summarizer.py`), and voice output (`voice_speaker.py`) are separated, independently testable components.
2. **Persistent caching** — a fallback disk cache (`visa_cache.json`) covers 21+ major UAE legal topics (Golden Visa, overstay fines, Emirates ID, family sponsorship, labour law, etc.) to handle rate limits and ensure demo stability.
3. **Universal webhook adapter** (`server.py`) accepts arbitrary payload shapes from ElevenLabs agent tools.

## Extensibility (v2 ideas)

1. **Direct GDRFA/ICP appointment booking** — OAuth integration to let users book medical fitness tests or typing-centre appointments by voice.
2. **Document upload & verification** — let users upload passport/visa scans to auto-check expiry or overstay fine calculations.
3. **WhatsApp voice integration** — connect the server to the Twilio WhatsApp API for async voice-note query processing.
