"""Apply only HUMAN-APPROVED review feedback -> revised cases. Strong/security cases preserved."""
import json
from .llm import get_client, extract_json, MODEL

SYSTEM = (
    "You are a senior QA engineer revising test cases using APPROVED feedback. Apply every "
    "approved point. Preserve strong cases (especially security/adversarial). "
    "Return ONLY a JSON array of about {n} cases — no prose, no fences. "
    "Each: {{id, title, type, preconditions, steps (array, max 4), expected}}. "
    "type in: positive|negative|edge|adversarial. State any assumption in preconditions."
)


def revise_cases(requirement, cases, approved, n=10, client=None):
    client = client or get_client()
    user = (
        f"Requirement:\n{requirement}\n\nCurrent cases:\n{json.dumps(cases, indent=2)}\n\n"
        f"Approved feedback:\n- " + "\n- ".join(approved)
    )
    resp = client.messages.create(
        model=MODEL, max_tokens=4096, system=SYSTEM.format(n=n),
        messages=[{"role": "user", "content": user}],
    )
    return extract_json(resp.content[0].text)
