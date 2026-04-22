from datetime import datetime, timedelta

import httpx
import pytest
import respx

from app.db import SessionLocal
from app.models import Carrier


def _mock_payload(allow="Y", status="A", name="HUB GROUP TRUCKING INC") -> dict:
    return {
        "content": [
            {
                "carrier": {
                    "legalName": name,
                    "allowedToOperate": allow,
                    "statusCode": status,
                    "dotNumber": 44110,
                }
            }
        ]
    }


@pytest.fixture(autouse=True)
def _clear_cache():
    from app.db import init_db

    init_db()
    with SessionLocal() as db:
        db.query(Carrier).delete()
        db.commit()


@respx.mock
def test_verify_eligible_carrier(authed_client):
    route = respx.get("https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/1515").mock(
        return_value=httpx.Response(200, json=_mock_payload())
    )
    r = authed_client.get("/carriers/verify?mc=MC-1515")
    assert r.status_code == 200
    body = r.json()
    assert body == {
        "eligible": True,
        "carrier_name": "HUB GROUP TRUCKING INC",
        "reason": "active",
        "mc_number": "1515",
    }
    assert route.called


@respx.mock
def test_verify_ineligible_not_authorized(authed_client):
    respx.get("https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/2222").mock(
        return_value=httpx.Response(200, json=_mock_payload(allow="N", status="I"))
    )
    r = authed_client.get("/carriers/verify?mc=2222")
    assert r.status_code == 200
    body = r.json()
    assert body["eligible"] is False
    assert "not_authorized" in body["reason"]


@respx.mock
def test_verify_empty_content_is_not_found(authed_client):
    respx.get("https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/99999").mock(
        return_value=httpx.Response(200, json={"content": []})
    )
    r = authed_client.get("/carriers/verify?mc=99999")
    assert r.status_code == 200
    body = r.json()
    assert body["eligible"] is False
    assert body["reason"] == "not_found"
    assert body["carrier_name"] is None


@respx.mock
def test_verify_caches_within_24h(authed_client):
    route = respx.get("https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/1515").mock(
        return_value=httpx.Response(200, json=_mock_payload())
    )
    r1 = authed_client.get("/carriers/verify?mc=1515")
    r2 = authed_client.get("/carriers/verify?mc=1515")
    assert r1.json() == r2.json()
    assert route.call_count == 1


@respx.mock
def test_verify_refetches_after_24h(authed_client):
    respx.get("https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/1515").mock(
        return_value=httpx.Response(200, json=_mock_payload())
    )
    authed_client.get("/carriers/verify?mc=1515")

    with SessionLocal() as db:
        c = db.query(Carrier).filter(Carrier.mc_number == "1515").first()
        c.fetched_at = datetime.utcnow() - timedelta(hours=25)
        db.commit()

    route2 = respx.get("https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/1515").mock(
        return_value=httpx.Response(200, json=_mock_payload())
    )
    authed_client.get("/carriers/verify?mc=1515")
    assert route2.called


@respx.mock
def test_verify_fmcsa_5xx_returns_503(authed_client):
    respx.get("https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/1515").mock(
        return_value=httpx.Response(500)
    )
    r = authed_client.get("/carriers/verify?mc=1515")
    assert r.status_code == 503


def test_verify_invalid_mc_format_returns_400(authed_client):
    r = authed_client.get("/carriers/verify?mc=abc")
    assert r.status_code == 400


def test_verify_rejects_missing_mc(authed_client):
    r = authed_client.get("/carriers/verify")
    assert r.status_code == 422
