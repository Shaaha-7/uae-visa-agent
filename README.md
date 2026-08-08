# 🇦🇪 UAE Visa & Government Intelligence AI Voice Agent

An intelligent, voice-powered AI assistant that allows anyone to ask questions about **UAE Visas, Emirates ID, Overstay Fines, Work Permits, and Government Laws** in natural speech (English, Arabic, Hindi, Urdu, etc.) and receive instant, verified answers spoken back in human voice.

---

## 🛠️ Setup & Working Instructions

### Prerequisites
- Python 3.10 or higher installed.

### 1. Installation
Clone the repository and install all dependencies:
```bash
git clone https://github.com/Shaaha-7/uae-visa-agent.git
cd uae-visa-agent/uae-visa-agent
pip install -r requirements.txt
```

### 2. Environment Variables Configuration
Create a `.env` file in the project root folder (`uae-visa-agent/uae-visa-agent/.env`) with the following keys:
```env
CONTEXT_DEV_API_KEY=your_context_dev_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
GROQ_API_KEY=your_groq_api_key
```

### 3. Run Command
Start the live webhook server:
```bash
python server.py
```
*The server will start on `http://localhost:5000` (expose port 5000 via ngrok or Cloudflare Tunnels for ElevenLabs Webhook integration).*

---

## 🏗️ Architecture Overview

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

---

## 💡 What It Does

1. **Voice-in / Voice-out Multilingual Interface**: Listens to user questions in English, Arabic, Hindi, Urdu, or French, and responds aloud in the user's native language using ElevenLabs TTS.
2. **Verified Live UAE Government Data**: Queries official government portals (`u.ae`, `icp.gov.ae`, `gdrfad.gov.ae`) via `context.dev` web extraction to ensure accurate, non-hallucinated visa rules, eligibility thresholds, and fee structures.
3. **Resilient Fallback Cache**: Maintains an updated, pre-compiled persistent disk cache (`visa_cache.json`) covering 21+ major UAE government categories (Golden Visa, Overstay Fines, Emirates ID, Family Sponsorship, Labour Law, etc.) to guarantee 100% uptime even if API credits are depleted.
