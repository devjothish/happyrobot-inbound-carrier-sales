from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Call
from app.schemas import CallIn, CallOut

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("", response_model=CallOut, status_code=201)
def create_call(payload: CallIn, db: Session = Depends(get_db)):
    data = payload.model_dump()
    data["call_id"] = data.get("call_id") or str(uuid.uuid4())
    if not data.get("started_at"):
        data["started_at"] = datetime.utcnow()
    row = Call(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return CallOut.model_validate(row)
