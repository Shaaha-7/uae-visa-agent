# test_llm.py
"""
Test Script for LLM Voice Summarizer Engine.
Tests raw context.dev extractions vs. LLM-formatted conversational responses.
"""

import json
from dotenv import load_dotenv

load_dotenv()

from gov_intel import UAEVisaIntelClient, LLMVoiceSummarizer


def run_llm_tests():
    client = UAEVisaIntelClient()
    llm = LLMVoiceSummarizer()

    test_questions = [
        "Which are the requirements for the UAE Golden Visa?",
        "How do I apply for the tourist visa as an Indian?",
        "How long will it take for the student's visa process?"
    ]

    print("=" * 70)
    print("           LLM VOICE SUMMARIZER ENGINE TEST")
    print("=" * 70)

    for i, q in enumerate(test_questions, 1):
        print(f"\n[TEST #{i} QUESTION]: \"{q}\"")
        print("-" * 70)

        # 1. Live Extraction via context.dev
        raw_result = client.smart_extract(q)
        data = raw_result.get("data", {})

        print("  [1. RAW CONTEXT.DEV EXTRACTION DATA]:")
        print(json.dumps(data, indent=2))

        # 2. LLM Conversational Speech Script
        llm_answer = llm.summarize_for_speech(q, data)

        print("\n  [2. GENERATED LLM CONVERSATIONAL VOICE RESPONSE]:")
        print(f"  \"{llm_answer}\"")
        print("=" * 70)


if __name__ == "__main__":
    run_llm_tests()
