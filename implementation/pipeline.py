import json
from typing import Callable, Optional
from .transcriber import transcribe_audio
from .interview_loop import run_interview_loop
from .schema import HemasSOP


def run_sop_pipeline(
    audio_path: str,
    ask_user: Callable[[str], str],
    on_progress: Optional[Callable] = None,
) -> dict:
    """
    Full pipeline: audio -> transcript -> structured SOP -> JSON dict.

    This is the main function that Engineer 1's Streamlit app calls.
    Returns a Python dict (JSON-serializable) that Engineers 3 and 4 consume.

    Args:
        audio_path: Path to the audio file from the Streamlit recorder.
        ask_user: Callback to ask the manager follow-up questions.
        on_progress: Optional callback for progress updates.

    Returns:
        A dict with keys matching HemasSOP fields. Guaranteed complete.
    """
    print("[Pipeline] Transcribing audio...")
    transcript = transcribe_audio(audio_path)
    print(f"[Pipeline] Transcript: {transcript[:100]}...")

    print("[Pipeline] Running interview loop...")
    sop: HemasSOP = run_interview_loop(
        initial_transcript=transcript,
        ask_user=ask_user,
        on_progress=on_progress,
    )

    sop_dict = sop.model_dump()

    with open("sop_output.json", "w") as f:
        json.dump(sop_dict, f, indent=2)

    print("[Pipeline] Done. SOP saved to sop_output.json")
    return sop_dict


if __name__ == "__main__":
    def console_ask(question: str) -> str:
        return input(f"\n? {question}\n-> Your answer: ")

    result = run_sop_pipeline(
        audio_path="test_audio.mp3",
        ask_user=console_ask,
    )
    print(f"\nFinal SOP:\n{json.dumps(result, indent=2)}")
