"""Thin, per-service spec for AeroAssist — the ONLY thing that changes per service.

The engine (adapters/python_api.py) is generic; onboarding a new service means writing a
spec like this: base URL, each endpoint's method/path, how a record maps to a request, and
the oracle for the expected result. GET/POST/DELETE is just a 'method' field.
"""
from .oracles import should_refund, is_well_formed
from .sut.app import BOOKINGS


def _cancel_oracle(r, resp, status):
    if not is_well_formed(r):
        return status in (400, 422)                      # malformed input MUST be rejected
    return status == 200 and resp.get("refund_allowed") == should_refund(r)


def _get_booking_oracle(r, resp, status):
    known = BOOKINGS.get(r["pnr"])                        # BOOKINGS = source of truth
    if known is None:
        return status == 404
    return (status == 200
            and resp.get("amount") == known["amount"]
            and resp.get("payment_status") == known["payment_status"])


AEROASSIST_SPEC = {
    "base_url": "",
    "endpoints": [
        {
            "name": "cancel_booking", "method": "POST", "path": "/cancel",
            "body_from_record": lambda r: {k: r.get(k) for k in
                ("pnr", "booking_time", "cancel_time", "amount", "payment_status")},
            "path_params": None,
            "expected_status": [200, 422, 400],
            "oracle": _cancel_oracle,
        },
        {
            "name": "get_booking", "method": "GET", "path": "/booking/{pnr}",
            "body_from_record": None,
            "path_params": lambda r: {"pnr": r["pnr"]},
            "expected_status": [200, 404],
            "oracle": _get_booking_oracle,
        },
    ],
}
