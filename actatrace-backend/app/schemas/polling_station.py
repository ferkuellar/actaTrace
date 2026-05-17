from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PollingStationCreate(BaseModel):
    polling_station_code: str = Field(pattern=r"^[A-Z0-9-]{6,80}$")
    state: str
    municipality: str
    district: str
    section: str
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    station_type: str
    status: str = "ACTIVE"


class PollingStationRead(ORMModel):
    id: str
    polling_station_code: str
    state: str
    municipality: str
    district: str
    section: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    station_type: str
    status: str
    created_at: datetime
    updated_at: datetime
