"""Seed the loads table with 50 realistic freight loads across major US lanes.

Run: python -m scripts.seed_loads
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

from app.db import SessionLocal, init_db
from app.models import Load

random.seed(42)

LANES = [
    ("Chicago, IL", "Atlanta, GA", 716),
    ("Los Angeles, CA", "Dallas, TX", 1435),
    ("Seattle, WA", "Denver, CO", 1316),
    ("New York, NY", "Miami, FL", 1280),
    ("Houston, TX", "Phoenix, AZ", 1170),
    ("Detroit, MI", "Nashville, TN", 533),
    ("Minneapolis, MN", "Kansas City, MO", 440),
    ("Boston, MA", "Raleigh, NC", 710),
    ("Portland, OR", "Salt Lake City, UT", 767),
    ("Philadelphia, PA", "Columbus, OH", 476),
    ("San Francisco, CA", "Las Vegas, NV", 569),
    ("Memphis, TN", "Indianapolis, IN", 465),
    ("Charlotte, NC", "Jacksonville, FL", 374),
    ("Dallas, TX", "Oklahoma City, OK", 206),
    ("St. Louis, MO", "Louisville, KY", 262),
    ("Cincinnati, OH", "Pittsburgh, PA", 288),
    ("Tampa, FL", "Birmingham, AL", 560),
    ("Albuquerque, NM", "Amarillo, TX", 289),
    ("Milwaukee, WI", "Omaha, NE", 493),
    ("Baltimore, MD", "Cleveland, OH", 371),
]

EQUIPMENT = [
    ("Dry Van", "48ft", 45000),
    ("Dry Van", "53ft", 45000),
    ("Reefer", "53ft", 43000),
    ("Flatbed", "48ft", 48000),
    ("Flatbed", "53ft", 48000),
    ("Step Deck", "48ft", 45000),
]

COMMODITIES_BY_EQUIPMENT = {
    "Dry Van": ["Electronics", "Textiles", "Packaged Goods", "Auto Parts", "Paper Products"],
    "Reefer": ["Produce", "Frozen Foods", "Dairy", "Pharmaceuticals", "Beverages"],
    "Flatbed": ["Steel Coils", "Lumber", "Machinery", "Building Materials", "Pipe"],
    "Step Deck": ["Tractors", "Industrial Equipment", "Prefab Structures"],
}


def _rate_per_mile(equipment: str) -> float:
    return {
        "Dry Van": (1.80, 2.40),
        "Reefer": (2.20, 3.00),
        "Flatbed": (2.10, 2.80),
        "Step Deck": (2.40, 3.20),
    }[equipment][0] + random.random() * 0.5


def build_loads(n: int = 50) -> list[Load]:
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    loads: list[Load] = []
    for i in range(n):
        origin, destination, miles = random.choice(LANES)
        equip_type, dims, max_weight = random.choice(EQUIPMENT)
        commodity = random.choice(COMMODITIES_BY_EQUIPMENT[equip_type])
        rate_mi = _rate_per_mile(equip_type)
        loadboard_rate = round(rate_mi * miles, 2)
        pickup_offset_hours = random.randint(12, 14 * 24)
        pickup = now + timedelta(hours=pickup_offset_hours)
        transit_hours = max(8, int(miles / 50))
        delivery = pickup + timedelta(hours=transit_hours)
        weight = random.randint(15000, max_weight)
        pieces = random.choice([1, 2, 4, 8, 12, 16, 22, 26])
        notes = random.choice(
            [
                "Dock high delivery",
                "Driver assist requested",
                "Temp 34F - reefer continuous",
                "No touch freight",
                "Team driver preferred",
                "",
                "Tarps required",
                "",
            ]
        ) if equip_type != "Reefer" else "Temp 34F - reefer continuous"
        loads.append(
            Load(
                load_id=f"LD-{i + 1:06d}",
                origin=origin,
                destination=destination,
                pickup_datetime=pickup,
                delivery_datetime=delivery,
                equipment_type=equip_type,
                loadboard_rate=loadboard_rate,
                notes=notes,
                weight=weight,
                commodity_type=commodity,
                num_of_pieces=pieces,
                miles=miles,
                dimensions=dims,
            )
        )
    return loads


def seed(n: int = 50) -> int:
    init_db()
    with SessionLocal() as db:
        db.query(Load).delete()
        db.add_all(build_loads(n))
        db.commit()
        count = db.query(Load).count()
    return count


if __name__ == "__main__":
    n = seed()
    print(f"Seeded {n} loads.")
