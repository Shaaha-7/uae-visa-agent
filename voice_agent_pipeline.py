# voice_agent_pipeline.py
"""
End-to-End Live Conversational Voice AI Pipeline:

  [User speaks into microphone]
       |
       v
  [ElevenLabs STT - Scribe v2] ───> Transcribed text
       |
       v
  [Context.dev Web Extraction] ───> Raw verified government JSON data
       |
       v
  [LLM Voice Summarizer Engine] ──> Warm, natural conversational speech script
       |
       v
  [ElevenLabs TTS] ───────────────> High-quality MP3 voice audio response
       |
       v
  [Real-Time Audio Playback]
"""

import json
import os
import sys
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

from gov_intel import (
    UAEVisaIntelClient,
    ContextDevError,
    ElevenLabsSpeaker,
    ElevenLabsError,
    LLMVoiceSummarizer
)


def play_audio(filepath: str):
    """Play an audio file using the default system player."""
    abs_path = os.path.abspath(filepath)
    if not os.path.exists(abs_path):
        print(f"  [PLAY] File not found: {abs_path}")
        return
    print(f"  [PLAY] Playing audio response: {abs_path}")
    try:
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            subprocess.call(["afplay", abs_path])
        else:
            subprocess.call(["xdg-open", abs_path])
    except Exception as e:
        print(f"  [PLAY] Could not auto-play: {e}")
        print(f"  [PLAY] Open the file manually: {abs_path}")


def process_single_turn(
    intel_client: UAEVisaIntelClient,
    speaker: ElevenLabsSpeaker,
    llm_summarizer: LLMVoiceSummarizer,
    user_question: str,
    output_audio_path: str = "voice_answer.mp3"
) -> bool:
    """
    Executes a single conversational turn:
    Query -> context.dev -> LLM Voice Summarizer -> ElevenLabs TTS -> Audio Playback.
    """
    print(f"\n============================================================")
    print(f" 🗣️  USER QUESTION: \"{user_question}\"")
    print(f"============================================================")

    # 1. Extract live facts via context.dev
    print("\n--- STEP 1: CONTEXT.DEV EXTRACTION (Live Gov Data) ---")
    try:
        intel_result = intel_client.smart_extract(user_question)
        extracted_data = intel_result.get("data", {})
        print("  -> Live data extracted successfully!")
        print(json.dumps(extracted_data, indent=2))
    except ContextDevError as e:
        print(f"  [ERROR] Context.dev extraction failed: {e}")
        return False

    # 2. LLM Summarizer (Synthesize warm conversational speech)
    print("\n--- STEP 2: LLM VOICE SUMMARIZER (Conversational Formatting) ---")
    spoken_text = llm_summarizer.summarize_for_speech(user_question, extracted_data)
    print(f"  -> LLM Speech Script: \"{spoken_text}\"")

    # 3. ElevenLabs TTS (Synthesize voice MP3)
    print("\n--- STEP 3: ELEVENLABS TTS (Voice Synthesis) ---")
    try:
        audio_file = speaker.generate_speech(spoken_text, output_path=output_audio_path)
    except ElevenLabsError as e:
        print(f"  [ERROR] ElevenLabs TTS failed: {e}")
        return False

    # 4. Play audio back to user
    print("\n--- STEP 4: REAL-TIME AUDIO PLAYBACK ---")
    play_audio(audio_file)
    return True


def run_live_conversational_agent(record_seconds: int = 8):
    """
    Continuous Live Conversational Loop:
    Keeps listening to the user, converting speech -> facts -> LLM -> voice response!
    """
    intel_client = UAEVisaIntelClient()
    speaker = ElevenLabsSpeaker()
    llm_summarizer = LLMVoiceSummarizer()

    print("============================================================")
    print("   🎙️  LIVE CONVERSATIONAL UAE VISA VOICE AI")
    print("   Continuous Voice Loop (Press Ctrl+C anytime to stop)")
    print("============================================================")

    turn_count = 0
    while True:
        turn_count += 1
        print(f"\n\n>>>>>>>> CONVERSATION TURN #{turn_count} <<<<<<<<")
        input("  Press [ENTER] when ready to speak your question...")

        try:
            # 1. Record voice
            audio_file = speaker.record_microphone(
                duration_seconds=record_seconds,
                output_path="user_voice_input.wav"
            )
            # 2. STT Transcription
            user_question = speaker.speech_to_text(audio_path=audio_file)

            if not user_question:
                print("  [WARN] No speech detected. Let's try again!")
                continue

            # 3. Full Turn Execution
            process_single_turn(
                intel_client=intel_client,
                speaker=speaker,
                llm_summarizer=llm_summarizer,
                user_question=user_question,
                output_audio_path=f"turn_{turn_count}_answer.mp3"
            )

        except KeyboardInterrupt:
            print("\n  Exiting Live Voice Conversation. Goodbye!")
            break
        except Exception as e:
            print(f"  [ERROR] An unexpected error occurred: {e}")
            time.sleep(1)


def run_text_interactive_agent():
    """
    Text-based interactive loop with LLM summarizer and ElevenLabs TTS output.
    """
    intel_client = UAEVisaIntelClient()
    speaker = ElevenLabsSpeaker()
    llm_summarizer = LLMVoiceSummarizer()

    print("============================================================")
    print("   💬 INTERACTIVE UAE VISA VOICE AGENT (Text Mode)")
    print("   Type your questions continuously (Type 'exit' or 'quit' to stop)")
    print("============================================================")

    turn_count = 0
    while True:
        turn_count += 1
        user_question = input(f"\n[Turn #{turn_count}] Type your visa question: ").strip()
        if not user_question or user_question.lower() in ["exit", "quit", "q"]:
            print("  Exiting agent. Goodbye!")
            break

        process_single_turn(
            intel_client=intel_client,
            speaker=speaker,
            llm_summarizer=llm_summarizer,
            user_question=user_question,
            output_audio_path=f"turn_{turn_count}_answer.mp3"
        )


if __name__ == "__main__":
    if "--text" in sys.argv:
        run_text_interactive_agent()
    else:
        seconds = 8
        for arg in sys.argv[1:]:
            if arg.isdigit():
                seconds = int(arg)
        run_live_conversational_agent(record_seconds=seconds)
