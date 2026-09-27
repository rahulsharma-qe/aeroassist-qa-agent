"""Reference adapter — BDD / Gherkin (.feature). Plain-English scenarios, NOT code.

This is Cucumber's Given/When/Then (English + step definitions) — a different layer from
REST Assured's fluent-Java given/when/then.
"""


def to_gherkin(package, verdict, well_formed, feature="Booking cancellation refund"):
    L = [
        f"Feature: {feature}",
        "  As a passenger, I can cancel within 24 hours of booking and receive a full refund",
        "",
    ]
    for r in package["data"]:
        rid, cat = r["id"], r.get("category")
        L += [f"  @{cat} @id_{rid}", f"  Scenario: Cancel booking {r.get('pnr')} ({cat})"]
        if not well_formed(r):
            L += [
                "    Given a cancellation request with missing or malformed fields",
                f"    When the passenger submits the cancellation for booking {r.get('pnr')}",
                "    Then the request is rejected as invalid input",
                "",
            ]
        else:
            outcome = "a full refund is issued" if verdict(r) else "no refund is issued"
            L += [
                f"    Given a booking {r.get('pnr')} booked at {r.get('booking_time')}",
                f'      And its payment status is "{r.get("payment_status")}"',
                f"      And the amount is {r.get('amount')}",
                f"    When the passenger cancels at {r.get('cancel_time')}",
                f"    Then {outcome}",
                "",
            ]
    return "\n".join(L)
