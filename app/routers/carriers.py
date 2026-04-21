from __future__ import annotations

from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Carrier
from app.schemas import VerifyResponse
from app.services.fmcsa import FMCSAError, fetch_mc, normalize_mc, parse_carrier

router = APIRouter(prefix="/carriers", tags=["carriers"])

CACHE_TTL = timedelta(hours=24)


@router.get("/verify", response_model=VerifyResponse)
async def verify_carrier(
    mc: str = Query(..., description="MC number (accepts 'MC-1515' or '1515')"),
    db: Session = Depends(get_db),
):
    try:
        mc_norm = normalize_mc(mc)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    cached = db.query(Carrier).filter(Carrier.mc_number == mc_norm).first()
    if cached and cached.fetched_at and cached.fetched_at > datetime.utcnow() - CACHE_TTL:
        return VerifyResponse(
            eligible=bool(cached.eligible),
            carrier_name=cached.carrier_name,
            reason=cached.reason or "cached",
            mc_number=mc_norm,
        )

    try:
        payload = await fetch_mc(mc_norm)
    except httpx.TimeoutException as e:
        raise HTTPException(status_code=503, detail="fmcsa timeout") from e
    except (FMCSAError, httpx.HTTPError) as e:
        raise HTTPException(status_code=503, detail=f"fmcsa error: {e}") from e

    eligible, name, reason = parse_carrier(payload)

    if cached:
        cached.carrier_name = name
        cached.eligible = 1 if eligible else 0
        cached.reason = reason
        cached.fetched_at = datetime.utcnow()
    else:
        db.add(
            Carrier(
                mc_number=mc_norm,
                carrier_name=name,
                eligible=1 if eligible else 0,
                reason=reason,
                fetched_at=datetime.utcnow(),
            )
        )
    db.commit()

    return VerifyResponse(
        eligible=eligible,
        carrier_name=name,
        reason=reason,
        mc_number=mc_norm,
    )
