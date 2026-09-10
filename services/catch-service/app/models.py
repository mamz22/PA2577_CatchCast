from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Catch(Base):
    __tablename__ = "catches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    species: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    length_cm: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    
    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    caught_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    temperature_c: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    humidity_percent: Mapped[int] = mapped_column(
            Integer,
            nullable=False,
        )

    wind_speed_mps: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    weather_observed_at: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )