# Technical Specification & System Architecture

This document contains technical details, component specifications, API schemas, execution flow, and design decisions for the **UAE Visa & Government Intelligence AI Voice Agent**.

---

## 🏗️ System Architecture Overview

The system consists of five decoupled layers:

```
[ ElevenLabs Agent / User Input ]
             │ (Webhook HTTP POST)
             ▼
      [ Flask Webhook ] (server.py)
             │
             ▼
  [ Smart Router & Client ] (gov_intel/uae_visa_client.py)
      ├── 1. Disk Cache Lookup (visa_cache.json)
      └── 2. Live Extractor (context.dev API)
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

## 🧩 Component Breakdown

### 1. Webhook Server (`server.py`)
- **Framework**: Flask
- **Endpoint**: `POST /api/visa-intel`
- **Port**: 5000 (Exposed via ngrok / Cloudflare Tunnels)
- **Role**: Normalizes incoming payloads from ElevenLabs Conversational AI Agents, extracts parameter keys (`question`, `query`, `input`), routes requests to `UAEVisaIntelClient` + `LLMVoiceSummarizer`, and formats multi-key JSON responses (`response`, `result`, `answer`, `output`) to satisfy ElevenLabs agent response parsing.

### 2. UAE Government Intelligence Client (`gov_intel/uae_visa_client.py`)
- **Source Constraints**: Strict URL binding to official domains (`u.ae`, `icp.gov.ae`, `gdrfad.gov.ae`, `mofa.gov.ae`).
- **Dynamic Extractor (`smart_extract`)**: Uses natural language keyword matching to select optimal target URLs and builds schema payloads for `context.dev` (`/v1/web/extract`).
- **Caching Mechanism**:
  - Persistent JSON file storage (`visa_cache.json`).
  - Fallback logic: If `context.dev` API credits are exhausted or HTTP timeout occurs, the client gracefully falls back to persistent cached records to maintain uptime.

### 3. LLM Voice Summarizer (`gov_intel/llm_summarizer.py`)
- **Primary Model**: Groq `llama-3.3-70b-versatile` (Fallback: OpenAI `gpt-4o-mini` / Rule-based template).
- **Language Detection**: Identifies language ISO code (English, Arabic, Hindi, Urdu, etc.) via low-token Groq call.
- **System Prompt Design**: Forces natural, warm, 2-to-3 sentence spoken output (60-80 words max) stripped of markdown formatting or bullet points for speech engines.

### 4. Voice Speaker Engine (`gov_intel/voice_speaker.py`)
- **STT**: ElevenLabs Scribe v2
- **TTS**: ElevenLabs `eleven_multilingual_v2` model
- **Audio Capture**: `sounddevice` + `scipy` for local microphone testing pipelines (`voice_agent_pipeline.py`).

---

## 🔌 Data Schemas & API Contracts

### `POST /api/visa-intel` Payload Schema (ElevenLabs Webhook)
```json
{
  "question": "What are the requirements for the UAE Golden Visa for real estate investors?"
}
```

### Server Response Schema (ElevenLabs Compatible Output)
```json
{
  "response": "To qualify for the 5-year Golden Visa as a real estate investor, you must own property in the UAE worth at least 2 million dirhams without mortgage loans. You can apply directly through the ICP Smart Services portal or GDRFA Dubai.",
  "result": "...",
  "answer": "...",
  "output": "..."
}
```

### Context.dev Extraction Request Schema (`POST /v1/web/extract`)
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

## 🛠️ Environment Variables Configuration

| Key | Description | Required |
|---|---|---|
| `CONTEXT_DEV_API_KEY` | Bearer token for context.dev web extraction API | Yes |
| `ELEVENLABS_API_KEY` | API key for ElevenLabs TTS / STT and Voice Agent | Yes |
| `ELEVENLABS_VOICE_ID` | Default Voice ID for TTS synthesis | Yes |
| `GROQ_API_KEY` | API key for Groq Llama-3.3 70B multilingual LLM | Yes |
| `OPENAI_API_KEY` | Optional fallback LLM key | No |

---

## 🔒 Security & Best Practices

- **API Secret Protection**: `.env` is listed in `.gitignore` to prevent credential leakage.
- **Input Sanitization**: Normalizes terminal encoding (`sys.stdout`) to prevent cp1252 character map crashes on non-ASCII scripts (Arabic, Devanagari).
- **HTTPS Transport**: HTTPS tunnels (ngrok / Cloudflare) are required as ElevenLabs webhooks enforce HTTPS strictly.
