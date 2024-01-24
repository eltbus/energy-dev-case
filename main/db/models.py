# -*-coding:utf8-*-
from datetime import date, datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import FLOAT, TIMESTAMP, Integer, String


class Base(DeclarativeBase):
    pass


class ParkRow(Base):
    __tableschema__ = "public"
    __tablename__ = "parks"
    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    timezone: Mapped[str] = mapped_column(String(50))
    energy_type: Mapped[str] = mapped_column(String(50))
    energy_readings: Mapped[List["EnergyReadingRow"]] = relationship(
        "EnergyReadingRow", back_populates="park", cascade="all, delete-orphan"
    )


class EnergyReadingRow(Base):
    __tableschema__ = "public"
    __tablename__ = "energy_readings"
    id: Mapped[Integer] = mapped_column(Integer, primary_key=True)
    megawatts: Mapped[float] = mapped_column(FLOAT)
    timestamp: Mapped[datetime] = mapped_column(TIMESTAMP)
    park_name: Mapped[str] = mapped_column(String(50), ForeignKey("parks.name"))
    park: Mapped["ParkRow"] = relationship("ParkRow", back_populates="energy_readings")


class StationRow(Base):
    __tableschema__ = "public"
    __tablename__ = "stations"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str]
    name: Mapped[str]
    province: Mapped[str]
    latitude: Mapped[str]
    longitude: Mapped[str]
    altitude: Mapped[str]

    measurements: Mapped[List["MeasurementRow"]] = relationship("MeasurementRow", back_populates="station")


class MeasurementRow(Base):
    __tableschema__ = "public"
    __tablename__ = "measurements"
    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[str] = mapped_column(ForeignKey("stations.id"))
    date: Mapped[date]
    avg_temp: Mapped[float]
    min_temp: Mapped[float]
    max_temp: Mapped[float]

    station: Mapped["StationRow"] = relationship("StationRow", back_populates="measurements")
