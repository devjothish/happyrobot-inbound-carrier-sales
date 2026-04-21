"""FMCSA carrier lookup + parsing.

API: https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc}?webKey={key}
Returns carrier status, operating authority, legal name. We classify as:
  - eligible: allowToOperate == 'Y' AND statusCode == 'A' (Active)
  - ineligible: otherwise
  - not_found: empty content array or 404
"""

from __future__ import annotations

import re

import httpx

from app.config import settings

FMCSA_BASE = "https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc}"


class FMCSAError(Exception):
    pass


def normalize_mc(raw: str) -> str:
    """Accept '1515', 'MC-1515', 'mc1515', ' MC 1515 '. Return digits only."""
    if not raw:
        raise ValueError("empty mc")
    digits = re.sub(r"\D", "", raw)
    if not digits:
        raise ValueError(f"no digits in mc: {raw!r}")
    if len(digits) > 8:
        raise ValueError(f"mc too long: {raw!r}")
    return digits


async def fetch_mc(mc: str) -> dict:
    url = FMCSA_BASE.format(mc=mc)
    async with httpx.AsyncClient(timeout=5.0) as cli:
        r = await cli.get(url, params={"webKey": settings.fmcsa_webkey})
        if r.status_code >= 500:
            raise FMCSAError(f"upstream {r.status_code}")
        r.raise_for_status()
        return r.json()


def parse_carrier(payload: dict) -> tuple[bool, str | None, str]:
    """Return (eligible, carrier_name, reason)."""
    content = payload.get("content")
    if not content:
        return False, None, "not_found"
    first = content[0] if isinstance(content, list) else content
    carrier = first.get("carrier") if isinstance(first, dict) else None
    if not carrier:
        return False, None, "malformed_response"
    name = carrier.get("legalName") or carrier.get("dbaName")
    allow = carrier.get("allowedToOperate") or carrier.get("allowToOperate")
    status = carrier.get("statusCode")
    if allow == "Y" and status == "A":
        return True, name, "active"
    reason = f"not_authorized(allow={allow},status={status})"
    return False, name, reason
