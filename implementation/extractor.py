from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .schema import HemasSOP

llm = ChatOpenAI(model="gpt-4o", temperature=0)
structured_llm = llm.with_structured_output(HemasSOP)

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert SOP (Standard Operating Procedure) analyst for Hemas, \
a Sri Lankan conglomerate. Your job is to extract structured SOP data from a manager's \
spoken description of a business process.

Extract as much information as possible from the text provided. If a field is not \
mentioned or cannot be reasonably inferred, set it to null — DO NOT guess or hallucinate.

Be thorough with steps: identify every discrete action the manager mentions in sequence.
Pay special attention to compliance fields: failure_protocols, backup_personnel, and \
escalation_path — these are mandatory for Hemas audit compliance.""",
    ),
    (
        "human",
        """Please extract the SOP data from this transcript:

--- TRANSCRIPT ---
{transcript}
--- END TRANSCRIPT ---

Extract all available information into the SOP schema. Set missing fields to null.""",
    ),
])

FOLLOWUP_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an SOP analyst. You have a partially completed SOP \
and the user has just answered a follow-up question about the missing field: {field}.
Update only the {field} field based on their answer. Preserve all other existing data exactly.""",
    ),
    (
        "human",
        """Existing SOP data: {existing_sop}

User's answer to the question about '{field}': {answer}

Return the complete updated SOP with {field} now filled in.""",
    ),
])


def extract_sop_from_transcript(transcript: str) -> HemasSOP:
    """
    Sends transcript to the LLM and returns a partially/fully filled HemasSOP.
    Fields the LLM could not find will be set to None.
    """
    chain = EXTRACTION_PROMPT | structured_llm
    result = chain.invoke({"transcript": transcript})
    return result


def extract_sop_from_followup(existing_sop: HemasSOP, followup_answer: str, missing_field: str) -> HemasSOP:
    """
    Takes the user's follow-up answer and merges it into the existing SOP object.
    Only updates the specific field that was missing.
    """
    chain = FOLLOWUP_PROMPT | structured_llm
    result = chain.invoke({
        "field": missing_field,
        "existing_sop": existing_sop.model_dump_json(),
        "answer": followup_answer,
    })
    return result
