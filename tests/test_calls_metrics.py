from datetime import datetime, timedelta

import pytest

from app.db import SessionLocal, init_db
from app.models import Call


@pytest.fixture(autouse=True)
def _clear():
    init_db()
    with SessionLocal() as db:
        db.query(Call).delete()
        db.commit()


def _make_call(**overrides):
    base = {
        "call_id": f"c-{overrides.get('seed', 'x')}",
        "mc_number": "1515",
        "carrier_name": "ACME TRANSPORT",
        "load_id": "LD-000001",
        "loadboard_rate": 2000.0,
        "final_agreed_rate": 2000.0,
        "negotiation_rounds": 0,
        "outcome": "booked",
        "sentiment": "positive",
        "duration_seconds": 180,
    }
    base.update(overrides)
    base.pop("seed", None)
    return base


def test_post_call_persists_with_generated_id(authed_client):
    payload = {
        "mc_number": "1515",
        "outcome": "booked",
        "sentiment": "positive",
        "loadboard_rate": 2000.0,
        "final_agreed_rate": 1950.0,
        "negotiation_rounds": 2,
        "duration_seconds": 200,
        "load_id": "LD-000001",
    }
    r = authed_client.post("/calls", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["call_id"]
    assert body["outcome"] == "booked"


def test_post_call_uses_provided_call_id(authed_client):
    payload = {"call_id": "abc-123", "outcome": "no_match"}
    r = authed_client.post("/calls", json=payload)
    assert r.status_code == 201
    assert r.json()["call_id"] == "abc-123"


def test_post_call_rejects_unknown_outcome(authed_client):
    r = authed_client.post("/calls", json={"outcome": "banana"})
    assert r.status_code == 422


def test_metrics_empty_returns_zeros(authed_client):
    r = authed_client.get("/metrics")
    assert r.status_code == 200
    m = r.json()
    assert m["total_calls"] == 0
    assert m["acceptance_rate"] == 0.0
    assert m["recent_calls"] == []


def test_metrics_after_calls(authed_client):
    calls_data = [
        _make_call(seed="1", outcome="booked", final_agreed_rate=1900.0),
        _make_call(seed="2", outcome="booked", final_agreed_rate=2000.0),
        _make_call(seed="3", outcome="negotiation_failed", sentiment="negative"),
        _make_call(seed="4", outcome="carrier_ineligible", sentiment="neutral"),
    ]
    for c in calls_data:
        authed_client.post("/calls", json=c)

    r = authed_client.get("/metrics")
    m = r.json()
    assert m["total_calls"] == 4
    assert m["acceptance_rate"] == 0.5
    assert m["outcome_breakdown"]["booked"] == 2
    assert m["outcome_breakdown"]["carrier_ineligible"] == 1
    # avg delta: ((1900-2000)/2000 + (2000-2000)/2000)/2 = -0.025
    assert m["avg_negotiated_delta_pct"] == -0.025
    assert m["mc_funnel"]["ineligible"] == 1
    assert any(x["sentiment"] == "negative" for x in m["sentiment_x_outcome"])


def test_metrics_recent_calls_desc_order(authed_client):
    base_time = datetime(2026, 4, 20, 10, 0, 0)
    for i in range(25):
        with SessionLocal() as db:
            db.add(
                Call(
                    call_id=f"c-{i:03d}",
                    started_at=base_time + timedelta(minutes=i),
                    outcome="booked",
                    loadboard_rate=2000.0,
                    final_agreed_rate=2000.0,
                    sentiment="positive",
                    duration_seconds=180,
                )
            )
            db.commit()

    r = authed_client.get("/metrics")
    recent = r.json()["recent_calls"]
    assert len(recent) == 20
    # Most recent first
    assert recent[0]["call_id"] == "c-024"
    assert recent[-1]["call_id"] == "c-005"
