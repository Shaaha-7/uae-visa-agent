# 🇦🇪 UAE Visa & Government Intelligence AI Voice Agent

Welcome! This is an intelligent, voice-powered AI assistant created to help anyone ask questions about **UAE Visas, Emirates ID, Overstay Fines, Work Permits, and Government Rules** — and get official, verified answers spoken back to them in natural, friendly voice in their own language (English, Arabic, Hindi, Urdu, etc.).

---

## 💡 What Does This Project Do? (In Simple Words)

Imagine having a friendly UAE government expert on the phone who:
- 🗣️ **Listens** when you speak your question in English, Arabic, Hindi, or any language.
- 🔍 **Checks** official UAE government portals (`u.ae`, `icp.gov.ae`, `gdrfad.gov.ae`) for the exact official rules.
- 🧠 **Translates & Summarizes** complex laws into 2 or 3 short, easy sentences.
- 🔊 **Speaks back to you** clearly in human voice!

No more reading through endless 20-page PDF legal guides or getting lost on confusing government websites.

---

## 🌟 Key Features

1. **Official Government Information**:
   - **Golden Visa**: Requirements for real estate investors (AED 2M), entrepreneurs, scientists, doctors, and students.
   - **Emirates ID**: Who needs it, step-by-step application steps, fees (AED 100/yr), and late renewal fines (AED 20/day).
   - **Overstay Fines**: Daily fine amounts (AED 50–100/day), grace periods, and re-entry ban rules.
   - **Family Sponsorship**: Minimum salary requirements (AED 4,000/month), required documents for spouse, kids, and parents.
   - **Other Visas**: Tourist, Green, Student, Retirement, Work, Transit, and Domestic Worker visas.
   - **General UAE Laws**: Labour law rules, gratuity calculations, free zone setup costs, driving licence conversion, and medical test steps.

2. **Multilingual Voice Support**:
   - Understands questions spoken in English, Arabic, Hindi, Urdu, French, Russian, etc.
   - Automatically detects your language and replies in that **exact same language**!

3. **Fast & Reliability Protection**:
   - Stores pre-verified official facts in a local cache so you get answers instantly without waiting.
   - If a new question is asked, it queries official UAE government portals via `context.dev`.

---

## 🚀 How to Run This Project (Step-by-Step for Beginners)

### Step 1: Install Python
Make sure you have **Python** installed on your computer. (Version 3.10 or newer).

### Step 2: Download or Clone this Repository
Open PowerShell or Terminal and run:
```bash
git clone https://github.com/Shaaha-7/uae-visa-agent.git
cd uae-visa-agent/uae-visa-agent
```

### Step 3: Install Required Dependencies
Run this single command:
```bash
pip install -r requirements.txt
```

### Step 4: Add Your API Keys
Create a file named `.env` in the project folder with your keys:
```env
CONTEXT_DEV_API_KEY=your_context_dev_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
GROQ_API_KEY=your_groq_key
```

### Step 5: Start the Voice Webhook Server
Run the server:
```bash
python server.py
```
Your server is now live and listening for questions! 🎉

---

## 📚 Technical Overview & Architecture

For software developers, engineers, or technical users interested in the full system design, API contracts, caching algorithms, context.dev web extraction schemas, and Groq LLM pipelines:

👉 **Please refer to [TECH_SPEC.md](file:///c:/Users/newadmin/Downloads/uae-visa-agent/uae-visa-agent/TECH_SPEC.md)** for complete technical documentation.

---

## 📄 License & Attribution
Data sourced from official UAE government portals:
- [U.AE (Official UAE Portal)](https://u.ae)
- [ICP (Federal Authority for Identity & Citizenship)](https://icp.gov.ae)
- [GDRFA Dubai](https://gdrfad.gov.ae)
