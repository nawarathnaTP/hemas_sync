# Hemas SOP Generator 

This module is responsible for taking a manager's voice recording and converting it into a fully structured Standard Operating Procedure (SOP) document. It is one component in a larger multi-engineer pipeline built for Hemas.

---

## What It Does

A manager records themselves verbally describing a business process. This module:

1. Transcribes the audio to text using OpenAI Whisper
2. Sends the transcript to GPT-4o to extract as much SOP data as possible automatically
3. Identifies any fields the transcript did not cover and asks follow-up questions
4. Outputs a complete, structured SOP as a Markdown file

---

## Architecture

```
Audio File
    │
    ▼
┌─────────────────┐
│  transcriber.py │  Sends audio to OpenAI Whisper API → returns raw transcript text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   extractor.py  │  Sends transcript to GPT-4o with structured output (LangChain)
│                 │  → returns a partially or fully filled HemasSOP object
└────────┬────────┘
         │
         ▼
┌──────────────────────┐
│  interview_loop.py   │  Checks which required fields are still None
│                      │  → asks the user targeted follow-up questions
│                      │  → calls extractor again to merge each answer back in
│                      │  → repeats until SOP is complete (max 10 iterations)
└────────┬─────────────┘
         │
         ▼
┌─────────────────┐
│    schema.py    │  Defines the HemasSOP Pydantic model — all fields, types,
│                 │  and which fields are required for audit compliance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   pipeline.py   │  Orchestrates all of the above into a single function call:
│                 │  run_sop_pipeline(audio_path, ask_user)
│                 │  This is what the Streamlit frontend (Engineer 1) calls
└─────────────────┘
```

### File breakdown

| File | Responsibility |
|---|---|
| `schema.py` | Pydantic data model for the SOP. Defines all fields and which are required. |
| `transcriber.py` | Calls OpenAI Whisper API to convert audio → text. |
| `extractor.py` | Calls GPT-4o via LangChain to extract structured SOP data from text. |
| `interview_loop.py` | Loop that identifies missing fields and asks follow-up questions to fill them. |
| `pipeline.py` | Top-level orchestrator. Entry point for other engineers to integrate with. |
| `test_implementation.py` | End-to-end test script using a mock transcript and pre-written answers — no audio or API keys needed for the extraction/interview stages. |

---

## SOP Fields

The SOP is divided into five sections:

**Header**
- `sop_title` — Name of the procedure
- `department` — Department it belongs to
- `sbu` — Hemas Strategic Business Unit (optional)

**Overview**
- `purpose` — Why the procedure exists
- `scope` — What it applies to and any exclusions
- `target_population` — Who follows this procedure

**Roles**
- `roles` — List of job titles and their responsibilities in this process

**Steps**
- `steps` — Ordered list of actions, who performs them, and what tools are used
- `tools_required` — All tools and systems referenced

**Compliance** *(required for Hemas audit)*
- `failure_protocols` — What to do if the process or a system fails
- `backup_personnel` — Who takes over if the primary person is unavailable
- `escalation_path` — Who to contact if a step cannot be completed

---

## Running Locally

### Prerequisites

- Python 3.12
- An OpenAI API key

### 1. Clone the repository

```bash
git clone <repo-url>
cd hemas_sync
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install langchain-openai langchain-core openai python-dotenv pydantic
```

### 4. Set up your API key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-your-key-here
```

### 5. Run the test script

```bash
python3 test_implementation.py
```

This runs a full end-to-end test using a built-in mock transcript and pre-written answers. No audio file or microphone needed. It will print three stages of output to the terminal and save the final SOP to `sop_output.md`.

### 6. View the output

Open `sop_output.md` in any Markdown viewer (VS Code, Notion, GitHub, etc.).

---

## Running with Real Audio

To use a real audio file instead of the mock transcript, call the pipeline directly:

```python
from implementation import run_sop_pipeline

def ask_user(question: str) -> str:
    return input(f"\n{question}\nYour answer: ")

result = run_sop_pipeline(
    audio_path="your_recording.mp3",
    ask_user=ask_user,
)
```

Supported audio formats: `.mp3`, `.wav`, `.m4a`, `.webm`
