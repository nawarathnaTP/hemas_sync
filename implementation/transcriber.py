import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio(audio_path: str) -> str:
    """
    Sends an audio file to OpenAI Whisper and returns the transcript.

    Args:
        audio_path: Path to the audio file (.wav, .mp3, .m4a, etc.)

    Returns:
        Transcribed text as a string.
    """
    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
            response_format="text",
        )
    return response.strip()


if __name__ == "__main__":
    transcript = transcribe_audio("test_audio.mp3")
    print(f"Transcript:\n{transcript}")
