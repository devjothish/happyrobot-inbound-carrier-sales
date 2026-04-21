from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text

from app.db import Base


class Load(Base):
    __tablename__ = "loads"

    load_id = Column(String, primary_key=True)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    pickup_datetime = Column(DateTime, nullable=False, index=True)
    delivery_datetime = Column(DateTime, nullable=False)
    equipment_type = Column(String, nullable=False, index=True)
    loadboard_rate = Column(Float, nullable=False)
    notes = Column(Text, default="")
    weight = Column(Integer, nullable=False)
    commodity_type = Column(String, nullable=False)
    num_of_pieces = Column(Integer, nullable=False)
    miles = Column(Integer, nullable=False)
    dimensions = Column(String, nullable=False)


class Carrier(Base):
    __tablename__ = "carriers"

    mc_number = Column(String, primary_key=True)
    carrier_name = Column(String)
    eligible = Column(Integer)
    reason = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow, index=True)


class Call(Base):
    __tablename__ = "calls"

    call_id = Column(String, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime)
    mc_number = Column(String, index=True)
    carrier_name = Column(String)
    load_id = Column(String, index=True)
    loadboard_rate = Column(Float)
    final_agreed_rate = Column(Float)
    negotiation_rounds = Column(Integer, default=0)
    outcome = Column(String, index=True)
    sentiment = Column(String, index=True)
    transcript = Column(Text)
    raw_extract = Column(JSON)
    duration_seconds = Column(Integer)
