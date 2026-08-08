# gov_intel/llm_summarizer.py
"""
LLM Voice Summarizer with Multilingual Support:
- Detects the language of the user's question automatically.
- Answers in the SAME language the user spoke (Arabic, Hindi, Urdu, English, etc.).
- Uses Groq (Llama 3.3 70B) for fast, high-quality multilingual responses.
- Falls back to OpenAI or a smart template if no LLM key is available.
"""

import os
import sys
import json
import requests
from typing import Optional


def _safe_print(label: str, text: str):
    """Print safely on Windows cp1252 terminals — replaces unrenderable chars with '?'."""
    safe = text.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8', errors='replace')
    print(f"{label}{safe}")


# Supported languages with their ElevenLabs-compatible STT codes
SUPPORTED_LANGUAGES = {
    "arabic": {"name": "Arabic", "stt_code": "ara", "greeting": "مرحباً"},
    "hindi": {"name": "Hindi", "stt_code": "hin", "greeting": "नमस्ते"},
    "urdu": {"name": "Urdu", "stt_code": "urd", "greeting": "آپ کا استقبال ہے"},
    "english": {"name": "English", "stt_code": "eng", "greeting": "Hello"},
    "french": {"name": "French", "stt_code": "fra", "greeting": "Bonjour"},
    "russian": {"name": "Russian", "stt_code": "rus", "greeting": "Привет"},
    "chinese": {"name": "Chinese", "stt_code": "zho", "greeting": "你好"},
}


class LLMVoiceSummarizer:
    """
    Multilingual LLM Summarizer:
    1. detect_language()    - Detects the language of the user's question via Groq.
    2. summarize_for_speech() - Generates a warm, natural, conversational spoken response
                                in the user's own language using Groq Llama 3.3 70B.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.openai_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.groq_key = os.environ.get("GROQ_API_KEY")

    # ─────────────────────────────────────────────────────────────
    # 1. LANGUAGE DETECTION
    # ─────────────────────────────────────────────────────────────

    def detect_language(self, text: str) -> str:
        """
        Detects the language of the user's question using Groq.
        Returns a lowercase language name e.g. 'arabic', 'hindi', 'english'.
        Falls back to 'english' if detection fails.
        """
        if not self.groq_key:
            return "english"

        detection_prompt = (
            "Detect the language of the following text and respond with ONLY the language name in lowercase English. "
            "Examples: 'english', 'arabic', 'hindi', 'urdu', 'french', 'russian', 'chinese'. "
            "Respond with just one word."
        )

        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": detection_prompt},
                        {"role": "user", "content": text}
                    ],
                    "max_tokens": 10
                },
                timeout=6
            )
            if resp.status_code == 200:
                detected = resp.json()["choices"][0]["message"]["content"].strip().lower()
                _safe_print("  [LANG DETECT] Detected language: ", detected)
                return detected
        except Exception as e:
            print(f"  [LANG DETECT] Detection failed: {e}")

        return "english"

    # ─────────────────────────────────────────────────────────────
    # 2. MULTILINGUAL VOICE SUMMARIZATION
    # ─────────────────────────────────────────────────────────────

    def summarize_for_speech(self, user_question: str, raw_extracted_data: dict) -> str:
        """
        Takes the user's question and raw context.dev JSON, detects the language,
        and synthesizes a concise, warm, conversational speech response in the user's language.
        """
        detected_language = self.detect_language(user_question)

        system_prompt = (
            f"You are a friendly, expert UAE Visa & Government Assistant speaking to a user over a live voice call. "
            f"IMPORTANT: The user's question is in {detected_language.upper()}. "
            f"You MUST respond in {detected_language.upper()} language ONLY. "
            f"Your task is to take the user's question and the raw verified government facts provided, "
            f"and create a warm, natural, 2-to-3 sentence spoken answer in {detected_language.upper()}. "
            f"Rules:\n"
            f"1. Respond ONLY in {detected_language.upper()} — not in any other language.\n"
            f"2. Be concise, direct, and conversational (optimized for voice speech).\n"
            f"3. Strictly use the provided government facts — do not invent or estimate rules.\n"
            f"4. Do not include markdown formatting, bullet points, or special symbols since this will be read aloud."
        )

        user_content = (
            f"User Question ({detected_language}): {user_question}\n\n"
            f"Extracted Government Facts (from official UAE portals):\n"
            f"{json.dumps(raw_extracted_data, indent=2)}"
        )

        # 1. Try Groq API (primary)
        if self.groq_key:
            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "max_tokens": 200
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    answer = resp.json()["choices"][0]["message"]["content"].strip()
                    _safe_print(f"  [LLM] Groq response ({detected_language}): ", answer[:80] + "...")
                    return answer
            except Exception as e:
                print(f"  [LLM] Groq API call failed: {e}")

        # 2. Try OpenAI API (fallback)
        if self.openai_key:
            try:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "max_tokens": 200
                    },
                    timeout=10
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"  [LLM] OpenAI API call failed: {e}")

        # 3. Smart conversational rule-based fallback (English only)
        return self._smart_fallback_summary(user_question, raw_extracted_data)

    # ─────────────────────────────────────────────────────────────
    # 3. FALLBACK TEMPLATE (English)
    # ─────────────────────────────────────────────────────────────

    def _smart_fallback_summary(self, question: str, data: dict) -> str:
        """
        Creates a clean, conversational fallback speech response if no LLM API key is set.
        """
        direct_ans = data.get("direct_answer")
        eligibility = data.get("eligibility_criteria") or []
        steps = data.get("application_steps") or []

        sentences = []

        if direct_ans:
            sentences.append(direct_ans)
        else:
            sentences.append(f"Here is what official UAE government portals state regarding {question}.")

        if eligibility:
            top_criteria = "; ".join(eligibility[:2])
            sentences.append(f"Key requirements include: {top_criteria}.")

        if steps:
            sentences.append(f"To apply, you can submit your application through {steps[0]}.")

        return " ".join(sentences)
