from datetime import datetime, timedelta

import pytest

from app.db import SessionLocal, init_db
from app.models import Load


@pytest.fixture(autouse=True)
def _seed(monkeypatch, tmp_path):
    # Fresh in-memory-ish DB per module.
    init_db()
    with SessionLocal() as db:
        db.query(Load).delete()
        now = datetime(2026, 4, 22, 8, 0, 0)
        db.add_all(
            [
                Load(
                    load_id="LD-TEST001",
                    origin="Chicago, IL",
                    destination="Atlanta, GA",
                    pickup_datetime=now + timedelta(days=1),
                    delivery_datetime=now + timedelta(days=2),
                    equipment_type="Dry Van",
                    loadboard_rate=1500.0,
                    notes="",
                    weight=30000,
                    commodity_type="Electronics",
                    num_of_pieces=10,
                    miles=716,
                    dimensions="53ft",
                ),
                Load(
                    load_id="LD-TEST002",
                    origin="Chicago, IL",
                    destination="Dallas, TX",
                    pickup_datetime=now + timedelta(days=2),
                    delivery_datetime=now + timedelta(days=3),
                    equipment_type="Reefer",
                    loadboard_rate=2200.0,
                    notes="Temp 34F",
                    weight=40000,
                    commodity_type="Produce",
                    num_of_pieces=20,
                    miles=925,
                    dimensions="53ft",
                ),
                Load(
                    load_id="LD-TEST003",
                    origin="Seattle, WA",
                    destination="Denver, CO",
                    pickup_datetime=now + timedelta(days=3),
                    delivery_datetime=now + timedelta(days=5),
                    equipment_type="Flatbed",
                    loadboard_rate=2800.0,
                    notes="Tarps required",
                    weight=45000,
                    commodity_type="Steel Coils",
                    num_of_pieces=4,
                    miles=1316,
                    dimensions="48ft",
                ),
                Load(
                    load_id="LD-TEST004",
                    origin="Chicago, IL",
                    destination="Nashville, TN",
                    pickup_datetime=now + timedelta(days=4),
                    delivery_datetime=now + timedelta(days=5),
                    equipment_type="Dry Van",
                    loadboard_rate=1200.0,
                    notes="",
                    weight=28000,
                    commodity_type="Textiles",
                    num_of_pieces=8,
                    miles=475,
                    dimensions="53ft",
                ),
            ]
        )
        db.commit()


def test_loads_search_returns_all_matching(authed_client):
    r = authed_client.get("/loads/search")
    assert r.status_code == 200
    data = r.json()
    assert "loads" in data
    assert len(data["loads"]) <= 3


def test_loads_search_filters_by_origin(authed_client):
    r = authed_client.get("/loads/search?origin=Chicago")
    assert r.status_code == 200
    loads = r.json()["loads"]
    assert len(loads) == 3
    assert all("Chicago" in load["origin"] for load in loads)


def test_loads_search_filters_by_destination(authed_client):
    r = authed_client.get("/loads/search?destination=Dallas")
    assert r.status_code == 200
    loads = r.json()["loads"]
    assert len(loads) == 1
    assert loads[0]["load_id"] == "LD-TEST002"


def test_loads_search_filters_by_equipment(authed_client):
    r = authed_client.get("/loads/search?equipment_type=Flatbed")
    assert r.status_code == 200
    loads = r.json()["loads"]
    assert len(loads) == 1
    assert loads[0]["equipment_type"] == "Flatbed"


def test_loads_search_case_insensitive(authed_client):
    r = authed_client.get("/loads/search?origin=chicago&equipment_type=dry van")
    assert r.status_code == 200
    loads = r.json()["loads"]
    assert len(loads) == 2


def test_loads_search_sorted_by_pickup(authed_client):
    r = authed_client.get("/loads/search?origin=Chicago")
    loads = r.json()["loads"]
    pickups = [load["pickup_datetime"] for load in loads]
    assert pickups == sorted(pickups)


def test_loads_get_by_id(authed_client):
    r = authed_client.get("/loads/LD-TEST002")
    assert r.status_code == 200
    data = r.json()
    assert data["load_id"] == "LD-TEST002"
    assert data["destination"] == "Dallas, TX"
    assert data["loadboard_rate"] == 2200.0


def test_loads_get_missing_returns_404(authed_client):
    r = authed_client.get("/loads/LD-DOES-NOT-EXIST")
    assert r.status_code == 404


def test_loads_search_by_reference_number_exact_match(authed_client):
    r = authed_client.get("/loads/search?reference_number=LD-TEST002")
    assert r.status_code == 200
    loads = r.json()["loads"]
    assert len(loads) == 1
    assert loads[0]["load_id"] == "LD-TEST002"


def test_loads_search_reference_number_overrides_other_filters(authed_client):
    # Even with a conflicting equipment_type filter, reference_number wins.
    r = authed_client.get(
        "/loads/search?reference_number=LD-TEST001&equipment_type=Flatbed"
    )
    assert r.status_code == 200
    loads = r.json()["loads"]
    assert len(loads) == 1
    assert loads[0]["load_id"] == "LD-TEST001"


def test_loads_search_unknown_reference_number_returns_empty(authed_client):
    r = authed_client.get("/loads/search?reference_number=LD-NOT-REAL")
    assert r.status_code == 200
    assert r.json()["loads"] == []
