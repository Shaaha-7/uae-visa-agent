import json
import os
from dotenv import load_dotenv

load_dotenv()

from gov_intel import UAEVisaIntelClient, ContextDevError, ElevenLabsSpeaker, ElevenLabsError


def main():
    client = UAEVisaIntelClient()
    speaker = ElevenLabsSpeaker()

    print("=" * 60)
    print("        UAE VISA AGENT - INTEL & VOICE ENGINE")
    print("=" * 60)

    question = "Which are the requirements for the UAE Golden Visa?"
    print(f"\n[QUESTION]: {question}")

    try:
        res = client.get_visa_requirements("golden visa")
        print("\n[LIVE ANSWER]:")
        print(json.dumps(res, indent=2))

        # ElevenLabs Voice Generation
        print("\n[ELEVENLABS VOICE GENERATION]:")
        if os.environ.get("ELEVENLABS_API_KEY"):
            audio_path = speaker.speak_visa_answer(
                question=question,
                response_data=res,
                output_path="golden_visa_summary.mp3"
            )
            print(f"-> Spoken answer audio saved to: {audio_path}")
        else:
            print("-> Skipping audio generation: ELEVENLABS_API_KEY is not set in .env")
            print("-> Add ELEVENLABS_API_KEY=your_key to .env to enable text-to-speech audio!")

    except ContextDevError as e:
        print(f"[FETCH ERROR]: {e}")
    except ElevenLabsError as e:
        print(f"[ELEVENLABS VOICE ERROR]: {e}")

    print("=" * 60)


if __name__ == "__main__":
    main()
