"""Domain oracles for AeroAssist — the single source of truth for expected results.

These are deterministic (rules, not an LLM) and are injected into every adapter, so Python,
Java, Gherkin, and Playwright all assert against the SAME truth. One oracle, many stacks.
"""
from dateutil import parser as dtparser

REFUND_WINDOW_HOURS = 24


def is_well_formed(r):
    """A record the API can process at all (right types on the fields it needs)."""
    return (
        isinstance(r.get("cancel_time"), str)
        and isinstance(r.get("booking_time"), str)
        and isinstance(r.get("pnr"), str)
        and isinstance(r.get("amount"), (int, float))
    )


def should_refund(r):
    """Computed oracle: should this cancellation get a full refund?"""
    if r.get("payment_status") in {"cancelled", "refunded"}:
        return False
    try:
        hrs = (dtparser.parse(r["cancel_time"]) - dtparser.parse(r["booking_time"])).total_seconds() / 3600.0
    except Exception:
        return False
    return 0 <= hrs <= REFUND_WINDOW_HOURS
