import uuid

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class PollingStation(TimestampMixin, Base):
    __tablename__ = "polling_stations"
    __table_args__ = (
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="ck_polling_latitude"),
        CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="ck_polling_longitude"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    polling_station_code: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    municipality: Mapped[str] = mapped_column(String(120), nullable=False)
    district: Mapped[str] = mapped_column(String(40), nullable=False)
    section: Mapped[str] = mapped_column(String(40), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500))
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    station_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE", nullable=False)

    actas = relationship("Acta", back_populates="polling_station")
    prep_results = relationship("PREPResult", back_populates="polling_station")
