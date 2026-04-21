from __future__ import annotations

from collections import Counter, defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Call
from app.schemas import CallOut

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
def get_metrics(db: Session = Depends(get_db)):
    calls: list[Call] = db.query(Call).order_by(Call.started_at.desc()).all()
    total = len(calls)

    if total == 0:
        return {
            "total_calls": 0,
            "acceptance_rate": 0.0,
            "avg_negotiated_delta_pct": 0.0,
            "outcome_breakdown": {},
            "mc_funnel": {"verified": 0, "ineligible": 0, "not_found": 0},
            "sentiment_x_outcome": [],
            "avg_time_to_book_seconds": 0,
            "avg_negotiation_rounds": 0.0,
            "recent_calls": [],
        }

    booked = [c for c in calls if c.outcome == "booked"]
    acceptance_rate = len(booked) / total

    deltas = []
    for c in booked:
        if c.loadboard_rate and c.final_agreed_rate:
            deltas.append((c.final_agreed_rate - c.loadboard_rate) / c.loadboard_rate)
    avg_delta = sum(deltas) / len(deltas) if deltas else 0.0

    outcome_breakdown = dict(Counter(c.outcome for c in calls))

    verified = sum(1 for c in calls if c.outcome not in ("carrier_ineligible",) and c.carrier_name)
    ineligible = sum(1 for c in calls if c.outcome == "carrier_ineligible")
    not_found = sum(
        1 for c in calls if c.outcome == "error" and not c.carrier_name and c.mc_number
    )
    mc_funnel = {"verified": verified, "ineligible": ineligible, "not_found": not_found}

    crosstab: dict[tuple[str, str], int] = defaultdict(int)
    for c in calls:
        if c.sentiment and c.outcome:
            crosstab[(c.sentiment, c.outcome)] += 1
    sentiment_x_outcome = [
        {"sentiment": s, "outcome": o, "count": n} for (s, o), n in crosstab.items()
    ]

    durations = [c.duration_seconds for c in booked if c.duration_seconds]
    avg_time_to_book = int(sum(durations) / len(durations)) if durations else 0

    rounds = [c.negotiation_rounds for c in booked if c.negotiation_rounds is not None]
    avg_rounds = sum(rounds) / len(rounds) if rounds else 0.0

    recent = [CallOut.model_validate(c).model_dump(mode="json") for c in calls[:20]]

    return {
        "total_calls": total,
        "acceptance_rate": round(acceptance_rate, 4),
        "avg_negotiated_delta_pct": round(avg_delta, 4),
        "outcome_breakdown": outcome_breakdown,
        "mc_funnel": mc_funnel,
        "sentiment_x_outcome": sentiment_x_outcome,
        "avg_time_to_book_seconds": avg_time_to_book,
        "avg_negotiation_rounds": round(avg_rounds, 2),
        "recent_calls": recent,
    }
