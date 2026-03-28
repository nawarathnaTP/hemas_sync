from typing import Callable, Optional
from .schema import HemasSOP
from .extractor import extract_sop_from_transcript, extract_sop_from_followup

FIELD_QUESTIONS = {
    "sop_title":         "What is the name or title of this procedure?",
    "department":        "Which department does this procedure belong to?",
    "sbu":               "Which Hemas business unit is this for (e.g. Morison Manufacturing, Hemas Mobility)?",
    "purpose":           "In one or two sentences, what is the purpose of this procedure? What problem does it solve?",
    "scope":             "Who and what does this procedure apply to? Are there any locations or situations that are excluded?",
    "target_population": "Who specifically follows this procedure? Which job roles or teams?",
    "roles":             "Who is involved in carrying out this procedure, and what is each person's responsibility?",
    "steps":             "Can you walk me through the procedure step by step, in order?",
    "failure_protocols": "What should happen if this process fails or a critical system goes down? What are the fallback actions?",
    "backup_personnel":  "If the primary person responsible is unavailable, who takes over?",
    "escalation_path":   "If someone cannot complete a step, who do they escalate to? What is the chain of contact?",
}

MAX_ITERATIONS = 10


def run_interview_loop(
    initial_transcript: str,
    ask_user: Callable[[str], str],
    on_progress: Optional[Callable[[HemasSOP, list], None]] = None,
) -> HemasSOP:
    """
    Main interview loop.

    1. Extracts initial data from transcript.
    2. Finds missing required fields.
    3. Asks the user for missing data.
    4. Merges answers back into the SOP.
    5. Repeats until complete or max iterations reached.

    Args:
        initial_transcript: Text from Whisper transcription.
        ask_user: A callable that accepts a question string and returns the user's text answer.
        on_progress: Optional callback called after each iteration with current SOP state.

    Returns:
        A complete HemasSOP object ready to be passed to Engineers 3 and 4.
    """
    print("[Engineer 2] Starting initial extraction...")
    sop = extract_sop_from_transcript(initial_transcript)

    iterations = 0
    while not sop.is_complete() and iterations < MAX_ITERATIONS:
        missing = sop.get_missing_fields()
        print(f"[Engineer 2] Missing fields: {missing}")

        if on_progress:
            on_progress(sop, missing)

        field_to_ask = missing[0]
        question = FIELD_QUESTIONS.get(
            field_to_ask,
            f"Can you provide more detail about '{field_to_ask}'?",
        )

        print(f"[Engineer 2] Asking: {question}")
        user_answer = ask_user(question)

        if not user_answer.strip():
            print("[Engineer 2] Empty answer received, skipping field.")
            iterations += 1
            continue

        sop = extract_sop_from_followup(sop, user_answer, field_to_ask)
        iterations += 1

    if not sop.is_complete():
        still_missing = sop.get_missing_fields()
        print(f"[Engineer 2] Warning: SOP still incomplete after {iterations} iterations. Missing: {still_missing}")
    else:
        print(f"[Engineer 2] SOP complete after {iterations} follow-up(s).")

    return sop
