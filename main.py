import os
from functools import reduce
from typing import List, Sequence, Dict
from datetime import datetime

from sqlalchemy import (
    select,
    create_engine,
    Column,
    VARCHAR,
    TIMESTAMP,
    INTEGER,
    FLOAT,
    ForeignKey,
    func as F,
)
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy.engine import RowMapping
from sqlalchemy.pool import StaticPool

Base = declarative_base()

username = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DB")
host = os.environ.get("POSTGRES_HOST", "127.0.0.1")
port = os.environ.get("POSTGRES_PORT", 5432)
DB_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"


class ParkRow(Base):
    __tableschema__ = "public"
    __tablename__ = "parks"
    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(50))
    energy_readings = relationship(
        "EnergyReadingRow", back_populates="park", cascade="all, delete-orphan"
    )


class EnergyReadingRow(Base):
    __tableschema__ = "public"
    __tablename__ = "energy_readings"
    id = Column(INTEGER, primary_key=True)
    value = Column(FLOAT)
    timestamp = Column(TIMESTAMP)
    park_id = Column(INTEGER, ForeignKey("parks.id"))
    park = relationship("ParkRow", back_populates="energy_readings")


engine = create_engine(DB_URL, future=True)

Base.metadata.create_all(engine)

with Session(engine, future=True) as session:
    spongebob = ParkRow(
        name="spongebob",
        EnergyReadingRow=[EnergyReadingRow(value=123, timestamp=datetime.now())],
    )
    sandy = ParkRow(
        name="sandy",
        EnergyReadingRow=[
            EnergyReadingRow(value=456, timestamp=datetime.now()),
            EnergyReadingRow(value=789, timestamp=datetime.now()),
        ],
    )
    session.add_all([spongebob, sandy])
    session.commit()

#############################################

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field


class EnergyReading(BaseModel):
    name: str
    value: float


class Park(BaseModel):
    name: str
    timezone: str
    energy_type: str
    metrics: List[EnergyReading] = Field(None)

    class Config:
        orm_mode = True


class Response(BaseModel):
    park: Park = Field(None, alias="ParkRow")
    energy_reading: EnergyReading = Field(None, alias="EnergyReadingRow")

    class Config:
        orm_mode = True


app = FastAPI()


def pack(d: Dict, i):
    energy_reading = {"value": i.name, "timestamp": i.timestamp}
    if d.get("name") is not None:
        d["energy_readings"].append(energy_reading)
    else:
        d["name"] = i.name
        d["energy_readings"] = [energy_reading]
    return d


def bar(engine):
    with Session(engine, future=True) as session:
        stmt = select(ParkRow.name)
        rows: Sequence[RowMapping] = session.execute(stmt).mappings().all()
        return rows


def foo(engine, park_id):
    with Session(engine, future=True) as session:
        stmt = (
            select(ParkRow.name, EnergyReadingRow.value, EnergyReadingRow.timestamp)
            .join(EnergyReadingRow)
            .where(ParkRow.id == park_id)
        )
        rows: Sequence[RowMapping] = session.execute(stmt).mappings().all()
        return reduce(pack, rows, {})


def eggs(engine):
    with Session(engine, future=True) as session:
        stmt = (
            select(
                ParkRow.name,
                F.min(EnergyReadingRow.value).label("min"),
                F.max(EnergyReadingRow.value).label("max"),
                F.sum(EnergyReadingRow.value).label("sum"),
                F.count(EnergyReadingRow.value).label("count"),
            )
            .join(EnergyReadingRow)
            .group_by(ParkRow.name)
        )
        rows: Sequence[RowMapping] = session.execute(stmt).mappings().all()
        return rows


@app.get("/")
def read_root():
    return RedirectResponse("docs")


@app.get("/parks")
def read_parks():
    return bar(engine)


@app.get("/parks/{park_id}")
def read_park(park_id: int):
    return foo(engine, park_id)


@app.get("stats")
def read_stats():
    return eggs(engine)
