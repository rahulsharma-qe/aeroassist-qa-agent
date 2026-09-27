"""Day-8 review gate — a SECOND LLM critiques the cases. The reviewer is also an LLM
and can over-correct or hallucinate, so a human is the final judge (see orchestrator)."""
import json
from .llm import get_client, extract_json, MODEL

SYSTEM = (
    "You are a meticulous QA reviewer auditing another engineer's test cases. "
    "Return ONLY JSON, no fences: {coverage_gaps:[..], ambiguities:[..], "
    "case_issues:[{id, issue}], verdict:'pass'|'needs_revision'}. Be specific and concise."
)


def review_gate(requirement, cases, client=None):
    client = client or get_client()
    user = f"Requirement:\n{requirement}\n\nTest cases:\n{json.dumps(cases, indent=2)}"
    resp = client.messages.create(
        model=MODEL, max_tokens=2000, system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    return extract_json(resp.content[0].text)
