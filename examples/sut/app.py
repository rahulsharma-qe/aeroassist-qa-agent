"""Mock System Under Test — a minimal AeroAssist cancellation/refund API.

This is a stand-in for the real service. It exposes two contracts so the framework can
prove it is method-agnostic:
  POST /cancel        -> takes a body, applies the 24h refund rule, returns a decision
  GET  /booking/{pnr} -> looks up a booking, returns it or 404

Explicit assumption: "within 24h" means <= 24h (boundary inclusive). The ambiguity was
named, not silently resolved.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dateutil import parser as dtparser

app = FastAPI(title="AeroAssist (mock SUT)")
REFUND_WINDOW_HOURS = 24

# tiny in-memory "database" so GET has a source of truth to look up
BOOKINGS = {
    "ABC123": {"pnr": "ABC123", "amount": 250.0, "payment_status": "active"},
    "XYZ789": {"pnr": "XYZ789", "amount": 175.5, "payment_status": "refunded"},
}


class CancelRequest(BaseModel):
    pnr: str
    booking_time: str
    cancel_time: str
    amount: float
    payment_status: str = "active"


@app.post("/cancel")
def cancel(req: CancelRequest):
    try:
        booked = dtparser.parse(req.booking_time)
        cancelled = dtparser.parse(req.cancel_time)
    except Exception:
        return {"refund_allowed": False, "refund_amount": 0.0, "reason": "invalid timestamps"}
    if req.payment_status in {"cancelled", "refunded"}:
        return {"refund_allowed": False, "refund_amount": 0.0, "reason": f"already {req.payment_status}"}
    hours = (cancelled - booked).total_seconds() / 3600.0
    if 0 <= hours <= REFUND_WINDOW_HOURS:
        return {"refund_allowed": True, "refund_amount": req.amount, "reason": "within 24h window"}
    return {"refund_allowed": False, "refund_amount": 0.0, "reason": "outside 24h window"}


@app.get("/booking/{pnr}")
def get_booking(pnr: str):
    booking = BOOKINGS.get(pnr)
    if booking is None:
        raise HTTPException(status_code=404, detail="booking not found")
    return booking
