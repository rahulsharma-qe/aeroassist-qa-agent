"""M11 — requirement -> structured test cases (positive/negative/edge/adversarial)."""
from .llm import get_client, extract_json, MODEL

SYSTEM = (
    "You are a senior QA engineer. Given a requirement, produce test cases covering "
    "positive, negative, edge, and adversarial scenarios. Generate about {n} cases. "
    "Return ONLY a JSON array — no prose, no fences, no trailing commas. "
    "Each case: {{id, title, type, preconditions, steps (array, max 4), expected}}. "
    "type in: positive | negative | edge | adversarial. Keep fields concise."
)


def generate_test_cases(requirement, n=8, client=None):
    client = client or get_client()
    resp = client.messages.create(
        model=MODEL, max_tokens=4096, system=SYSTEM.format(n=n),
        messages=[{"role": "user", "content": f"Requirement:\n{requirement}"}],
    )
    return extract_json(resp.content[0].text)
