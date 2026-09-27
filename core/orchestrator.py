"""The QA agent — orchestrates the core into one flow and emits a framework-agnostic package.

Two autonomy modes on one flag:
  human_in_the_loop=True   -> pause at the review gate for live human triage (new features)
  human_in_the_loop=False  -> apply a pre-approved policy end-to-end (regression / CI)

The validator ACTS (not just reports): weak/failing data -> one bounded retry -> honest flag.
"""
from .generate_cases import generate_test_cases
from .review_gate import review_gate
from .revise_cases import revise_cases
from .generate_data import generate_test_data
from .validate_data import validate_data


# Pre-approved policy used in AUTO / CI mode (human judgment, frozen once).
DEFAULT_APPROVED_FEEDBACK = [
    "Add coverage: cancellation near midnight / timezone boundary.",
    "Add coverage: rapid successive cancellation attempts (race condition).",
    "Add coverage: payment gateway unavailable during cancellation.",
    "Clarify & test the 24h window as booking-CREATION time (state the assumption).",
    "Add an explicit assumption + case for whether 'full refund' includes fees.",
    "Make boundary conditions exact (e.g., 86400 seconds), not vague.",
    "Remove any invented payment-method constraints; keep payment-method agnostic.",
    "KEEP all security/adversarial tests (do NOT drop them as out-of-scope).",
]


def _human_triage(review):
    """Show critic feedback; let a human approve only what's real (CLI input)."""
    items = list(review.get("coverage_gaps", [])) + list(review.get("ambiguities", []))
    items += [f"[{c['id']}] {c['issue']}" for c in review.get("case_issues", [])]
    print("\n[HUMAN GATE] critic points:")
    for i, it in enumerate(items, 1):
        print(f"  {i}. {it}")
    choice = input("Approve numbers / 'all' / 'none': ").strip().lower()
    if choice == "all":
        return items
    if choice == "none":
        return []
    import re
    idxs = [int(x) for x in re.findall(r"\d+", choice)]
    return [items[i - 1] for i in idxs if 1 <= i <= len(items)]


def orchestrate(requirement, client=None, human_in_the_loop=False, max_data_retries=1):
    log = []

    def step(msg):
        log.append(msg)
        print("-", msg)

    print("=" * 60)
    print(f"QA AGENT | mode = {'HUMAN-IN-THE-LOOP' if human_in_the_loop else 'AUTO/CI'}")
    print("=" * 60)

    cases = generate_test_cases(requirement, client=client)
    step(f"generated {len(cases)} test cases")

    review = review_gate(requirement, cases, client=client)
    step(f"review verdict: {review['verdict']}")

    if human_in_the_loop:
        approved = _human_triage(review)
    else:
        approved = DEFAULT_APPROVED_FEEDBACK
        step(f"auto-applied {len(approved)} pre-approved policy points")

    if approved:
        cases = revise_cases(requirement, cases, approved, client=client)
        step(f"revised to {len(cases)} cases after approved feedback")

    flag = None
    for attempt in range(max_data_retries + 1):
        data = generate_test_data(requirement, cases, client=client)
        step(f"generated {len(data)} data records (attempt {attempt + 1})")
        passed, rule_issues, judgment = validate_data(data, client=client)
        step(f"validation: {len(rule_issues)} rule issue(s), variety={judgment['variety']}")
        if passed:
            break
        if attempt < max_data_retries:
            step("weak/failing -> retrying once (non-determinism may fix it)")
        else:
            flag = "weak — review before use"
            step("still weak after retry -> FLAGGING package (not blocking)")

    return {
        "requirement": requirement,
        "cases": cases,
        "data": data,
        "validation": {"rule_issues": rule_issues, "llm_judgment": judgment},
        "meta": {
            "mode": "hitl" if human_in_the_loop else "auto",
            "n_cases": len(cases), "n_data": len(data),
            "data_quality_flag": flag, "log": log,
        },
    }
