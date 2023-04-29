# -*-coding:utf8-*-
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.types import FLOAT, Integer, TIMESTAMP, String


class Base(DeclarativeBase):
    pass


class ParkRow(Base):
    __tableschema__ = "public"
    __tablename__ = "parks"
    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    timezone: Mapped[str] = mapped_column(String(50))
    energy_type: Mapped[str] = mapped_column(String(50))
    energy_readings: Mapped[List["EnergyReadingRow"]] = relationship("EnergyReadingRow", back_populates="park", cascade="all, delete-orphan")


class EnergyReadingRow(Base):
    __tableschema__ = "public"
    __tablename__ = "energy_readings"
    id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
    megawatts: Mapped[float] = mapped_column(FLOAT)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP)
    park_name: Mapped[str] = mapped_column(String(50), ForeignKey("parks.name"))
    park: Mapped["ParkRow"] = relationship("ParkRow", back_populates="energy_readings")
