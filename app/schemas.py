from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class LoadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    notes: str | None = ""
    weight: int
    commodity_type: str
    num_of_pieces: int
    miles: int
    dimensions: str


class LoadSearchResponse(BaseModel):
    loads: list[LoadOut]


class VerifyResponse(BaseModel):
    eligible: bool
    carrier_name: str | None = None
    reason: str
    mc_number: str


Outcome = Literal[
    "booked",
    "no_match",
    "carrier_ineligible",
    "negotiation_failed",
    "carrier_walked",
    "error",
]
Sentiment = Literal["positive", "neutral", "negative"]


class CallIn(BaseModel):
    call_id: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    mc_number: str | None = None
    carrier_name: str | None = None
    load_id: str | None = None
    loadboard_rate: float | None = None
    final_agreed_rate: float | None = None
    negotiation_rounds: int = 0
    outcome: Outcome
    sentiment: Sentiment | None = None
    duration_seconds: int | None = None
    transcript: str | None = None
    raw_extract: dict | None = None


class CallOut(CallIn):
    model_config = ConfigDict(from_attributes=True)

    call_id: str
