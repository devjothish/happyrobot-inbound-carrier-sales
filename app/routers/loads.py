from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Load
from app.schemas import LoadOut, LoadSearchResponse

router = APIRouter(prefix="/loads", tags=["loads"])


@router.get("/search", response_model=LoadSearchResponse)
def search_loads(
    origin: str | None = Query(default=None),
    destination: str | None = Query(default=None),
    equipment_type: str | None = Query(default=None),
    pickup_date: date | None = Query(default=None),
    reference_number: str | None = Query(
        default=None,
        description="Exact-match load identifier (e.g. LD-000042). "
        "If provided, other filters are ignored.",
    ),
    limit: int = Query(default=3, ge=1, le=10),
    db: Session = Depends(get_db),
):
    q = db.query(Load)
    if reference_number:
        q = q.filter(Load.load_id == reference_number.strip())
    else:
        if origin:
            q = q.filter(func.lower(Load.origin).like(f"%{origin.lower()}%"))
        if destination:
            q = q.filter(func.lower(Load.destination).like(f"%{destination.lower()}%"))
        if equipment_type:
            q = q.filter(func.lower(Load.equipment_type) == equipment_type.lower())
        if pickup_date:
            q = q.filter(func.date(Load.pickup_datetime) == pickup_date)
    rows = q.order_by(Load.pickup_datetime.asc()).limit(limit).all()
    return {"loads": [LoadOut.model_validate(r) for r in rows]}


@router.get("/{load_id}", response_model=LoadOut)
def get_load(load_id: str, db: Session = Depends(get_db)):
    row = db.query(Load).filter(Load.load_id == load_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="load not found")
    return LoadOut.model_validate(row)
