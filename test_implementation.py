from implementation.extractor import extract_sop_from_transcript, extract_sop_from_followup
from implementation.interview_loop import FIELD_QUESTIONS

MOCK_TRANSCRIPT = """
So basically what we do is, when a new vehicle comes in for servicing,
the service advisor checks it in on the DMS system. They do a walkaround
inspection and note any damages. Then the vehicle goes to the workshop
supervisor who assigns it to a technician. The technician does the work
based on the job card. When done, the quality inspector checks it.
Then we call the customer for pickup.
"""

MOCK_ANSWERS = {
    "name or title":        "Vehicle Service Intake and Delivery Procedure",
    "department":           "After-Sales / Service Department",
    "purpose":              "To ensure vehicles are received, serviced, and returned to customers in a consistent and quality-controlled manner.",
    "apply to":             "Applies to all vehicles brought in for servicing at the workshop. Excludes vehicles requiring accident repairs or body work.",
    "specifically follows": "Service advisors, workshop supervisors, technicians, and quality inspectors at the service centre.",
    "fallback":             "If the DMS system is down, job cards are filled out manually. The workshop supervisor holds the vehicle until the system is restored.",
    "unavailable":          "The senior service advisor covers for the service advisor. The workshop manager covers for the workshop supervisor.",
    "escalate":             "Escalate to the workshop supervisor first, then to the branch manager if unresolved. Contact via internal phone or WhatsApp group.",
}

def mock_user(q: str) -> str:
    for key, val in MOCK_ANSWERS.items():
        if key in q.lower():
            return val
    return "Not specified."


# ─────────────────────────────────────────────
# STAGE 1: Initial LLM extraction from transcript
# ─────────────────────────────────────────────
print("=" * 60)
print("STAGE 1: INITIAL LLM EXTRACTION FROM TRANSCRIPT")
print("=" * 60)

sop = extract_sop_from_transcript(MOCK_TRANSCRIPT)
sop_data = sop.model_dump()

print("\nFields extracted from transcript:")
for field, value in sop_data.items():
    if value is not None:
        print(f"  [FILLED] {field}: {value}")

print("\nFields the LLM could not find:")
for field in sop.get_missing_fields():
    print(f"  [MISSING] {field}")


# ─────────────────────────────────────────────
# STAGE 2: Follow-up questions for missing fields
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 2: FOLLOW-UP QUESTIONS FOR MISSING FIELDS")
print("=" * 60)

MAX_ITERATIONS = 10
iterations = 0

while not sop.is_complete() and iterations < MAX_ITERATIONS:
    missing = sop.get_missing_fields()
    field = missing[0]
    question = FIELD_QUESTIONS.get(field, f"Can you provide more detail about '{field}'?")
    answer = mock_user(question)

    print(f"\n  Field:    {field}")
    print(f"  Question: {question}")
    print(f"  Answer:   {answer}")

    sop = extract_sop_from_followup(sop, answer, field)

    updated_value = getattr(sop, field)
    if updated_value is not None:
        print(f"  Result:   [FILLED] -> {updated_value}")
    else:
        print(f"  Result:   [STILL MISSING] LLM could not extract a value from the answer")

    iterations += 1


# ─────────────────────────────────────────────
# STAGE 3: Final SOP
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("STAGE 3: FINAL SOP")
print("=" * 60)
print(f"\nComplete: {sop.is_complete()}")
print(f"Still missing: {sop.get_missing_fields()}")

sop_data = sop.model_dump()
lines = []
lines.append(f"# {sop_data.get('sop_title', 'Untitled SOP')}\n")
lines.append(f"**Department:** {sop_data.get('department', 'N/A')}  ")
if sop_data.get('sbu'):
    lines.append(f"**SBU:** {sop_data.get('sbu')}  ")
lines.append("\n---\n")
lines.append("## Purpose\n")
lines.append(f"{sop_data.get('purpose', 'N/A')}\n")
lines.append("\n## Scope\n")
lines.append(f"{sop_data.get('scope', 'N/A')}\n")
lines.append("\n## Target Population\n")
lines.append(f"{sop_data.get('target_population', 'N/A')}\n")
lines.append("\n## Roles and Responsibilities\n")
for role in sop_data.get('roles') or []:
    lines.append(f"- **{role['title']}:** {role['responsibility']}")
lines.append("\n## Tools Required\n")
for tool in sop_data.get('tools_required') or []:
    lines.append(f"- {tool}")
lines.append("\n## Procedure Steps\n")
for step in sop_data.get('steps') or []:
    tools = f" *(Tools: {step['tools_or_systems']})*" if step.get('tools_or_systems') else ""
    lines.append(f"{step['step_number']}. **{step['action']}** — {step['responsible_role']}{tools}")
lines.append("\n---\n")
lines.append("## Compliance\n")
lines.append(f"**Failure Protocols:** {sop_data.get('failure_protocols', 'N/A')}\n")
lines.append(f"**Backup Personnel:** {sop_data.get('backup_personnel', 'N/A')}\n")
lines.append(f"**Escalation Path:** {sop_data.get('escalation_path', 'N/A')}\n")

with open("sop_output.md", "w") as f:
    f.write("\n".join(lines))
print("\nSOP saved to sop_output.md")
