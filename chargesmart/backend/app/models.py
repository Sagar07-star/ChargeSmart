from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now(): return datetime.now(timezone.utc)
class Station(Base):
    __tablename__ = 'stations'
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str]
    address: Mapped[str]
    lat: Mapped[float]
    lon: Mapped[float]
    operator: Mapped[str]
    power_kw: Mapped[float]
    connectors: Mapped[list] = mapped_column(JSON)
    ports: Mapped[int]
    status: Mapped[str] = mapped_column(default='Status Unknown')
    tariff: Mapped[float | None]
    source: Mapped[str]
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class Connector(Base):
    __tablename__ = 'connectors'
    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str] = mapped_column(ForeignKey('stations.id'))
    kind: Mapped[str]
    power_kw: Mapped[float]
class Vehicle(Base):
    __tablename__ = 'vehicles'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    capacity: Mapped[float]
    efficiency: Mapped[float]
    connector: Mapped[str]
    max_charge_kw: Mapped[float]
class Report(Base):
    __tablename__ = 'reports'
    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str] = mapped_column(ForeignKey('stations.id'))
    issue: Mapped[str]
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class SavedRoute(Base):
    __tablename__ = 'saved_routes'
    id: Mapped[int] = mapped_column(primary_key=True)
    guest_id: Mapped[str]
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
class ChargingSession(Base):
    __tablename__ = 'charging_sessions'
    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str] = mapped_column(ForeignKey('stations.id'))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    duration: Mapped[float]
    synthetic: Mapped[int] = mapped_column(default=1)
class UsageHistory(Base):
    __tablename__ = 'usage_history'
    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str] = mapped_column(ForeignKey('stations.id'))
    hour: Mapped[int]
    occupancy: Mapped[float]
    wait_minutes: Mapped[float]
    source: Mapped[str] = mapped_column(default='synthetic')
class PredictionRecord(Base):
    __tablename__ = 'prediction_records'
    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str]
    minutes: Mapped[float]
    source: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
