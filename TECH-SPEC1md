# Technical Specification: UAE Visa & Government Intelligence AI Voice Agent

## 01 Problem

Navigating UAE immigration laws, visa eligibility, Emirates ID rules, and overstay fine structures is notoriously complex. Expats, tourists, employers, and elderly residents face fragmented government portals, legal jargon, and language barriers (especially non-English/non-Arabic speakers). 

**Why Voice?**
Immigration queries are urgent and personal. Users often seek quick answers while traveling or multi-tasking. A voice interface lowers accessibility barriers for non-tech-savvy users and enables natural multi-lingual spoken conversation in their native language (Hindi, Urdu, Arabic, English, etc.).

---

## 02 Architecture

```
[ User Spoken Voice Input ]
             │
             ▼
[ ElevenLabs Conversational AI Agent ] ──(Multilingual STT/TTS)
             │
             ▼ (Webhook POST /api/visa-intel)
  [ Flask Webhook Server ] (server.py)
             │
             ▼
 [ Smart Extractor & Router ] (gov_intel/uae_visa_client.py)
      ├── 1. Persistent Cache Lookup (visa_cache.json)
      └── 2. Live Extractor via context.dev (Web API) -> Official UAE Portals (u.ae, icp.gov.ae)
             │ (Extracted JSON)
             ▼
 [ Groq LLM Summarizer ] (gov_intel/llm_summarizer.py)
      ├── 1. Language Detector (Llama-3.3-70B)
      └── 2. Speech Script Synthesizer (2-3 concise sentences)
             │ (Spoken Response Text)
             ▼
[ ElevenLabs Spoken Voice Response to User ]
```

---

## 03 Tool Rationale

- **ElevenLabs**: Used for state-of-the-art Multilingual Text-to-Speech (`eleven_multilingual_v2`), Scribe v2 Speech-to-Text, and real-time Webhook tool integration capabilities with ultra-low latency.
- **context.dev**: Specifically chosen because traditional search APIs return unstructured blog posts or agency ads. `context.dev` allows schema-driven extraction directly from official government portals (`u.ae`, `icp.gov.ae`, `gdrfad.gov.ae`), guaranteeing non-hallucinated legal facts.
- **Groq (`llama-3.3-70b-versatile`)**: Provides near-instant inference speed (~200ms) for language detection and conversational response synthesis, keeping voice turn-taking response times under 1.5 seconds.

---

## 04 Feasibility

To deliver a fully functional, production-ready system within the 6-hour build window:
1. **Modular Architecture**: Separated web extraction (`uae_visa_client.py`), LLM summarization (`llm_summarizer.py`), and voice output (`voice_speaker.py`).
2. **Persistent Caching**: Built a fallback disk cache (`visa_cache.json`) for 21+ major UAE legal topics (Golden Visa, Overstay Fines, Emirates ID, Family Sponsorship, Labour Law, etc.) to handle rate limits and ensure 100% demo stability.
3. **Flask Webhook Interoperability**: Built a universal webhook adapter (`server.py`) accepting arbitrary payload shapes from ElevenLabs Agent tools.

---

## 05 Extensibility

What **v2** will feature:
1. **Direct GDRFA/ICP Appointment Booking**: Integrating OAuth authentication to let users book medical fitness tests or typing centre appointments directly via voice.
2. **Document Upload & Verification**: Allowing users to upload passport/visa scans to automatically check visa expiry or overstay fine calculations.
3. **WhatsApp Voice Integration**: Connecting the server to Twilio WhatsApp API for async voice note query processing.
