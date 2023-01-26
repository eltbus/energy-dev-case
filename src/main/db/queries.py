from datetime import datetime
from typing import List, Sequence

from sqlalchemy import func as F
from sqlalchemy import select
from sqlalchemy.engine import RowMapping
from sqlalchemy.orm import Session
from sqlalchemy.types import DATE

from main.constraints import EnergyType, ParkName, Timezone
from main.db.models import EnergyReadingRow, ParkRow


def selectParks(
    session: Session, timezones: List[Timezone], energy_types: List[EnergyType], offset: int, limit: int
) -> Sequence[RowMapping]:
    stmt = select(ParkRow.name, ParkRow.timezone, ParkRow.energy_type).offset(offset).limit(limit)
    match (not timezones, not energy_types):
        case (True, True):
            pass
        case (True, False):
            stmt = stmt.where(ParkRow.energy_type.in_(energy_types)) # type:ignore
        case (False, True):
            stmt = stmt.where(ParkRow.timezone.in_(timezones)) # type:ignore
        case (False, False):
            stmt = stmt.where(ParkRow.timezone.in_(timezones)).where(ParkRow.energy_type.in_(energy_types)) # type:ignore
    return session.execute(stmt).mappings().all()


def selectParksWithEnergyReadings(
    session: Session,
    park_names: List[ParkName],
    timezones: List[Timezone],
    energy_types: List[EnergyType],
    offset: int,
    limit: int,
) -> Sequence[RowMapping]:
    stmt = (
        select(
            ParkRow.name, ParkRow.timezone, ParkRow.energy_type, EnergyReadingRow.megawatts, EnergyReadingRow.timestamp
        )
        .offset(offset)
        .limit(limit)
        .join(EnergyReadingRow)
    )
    match (not park_names, not timezones, not energy_types):
        case (True, True, True):
            pass
        case (True, True, False):
            stmt = stmt.where(ParkRow.energy_type.in_(energy_types)) # type:ignore
        case (True, False, True):
            stmt = stmt.where(ParkRow.timezone.in_(timezones)) # type:ignore
        case (True, False, False):
            stmt = stmt.where(ParkRow.timezone.in_(timezones)).where(ParkRow.energy_type.in_(energy_types)) # type:ignore
        case (False, True, True):
            stmt = stmt.where(ParkRow.name.in_(park_names)) # type:ignore
        case (False, True, False):
            stmt = stmt.where(ParkRow.name.in_(park_names)).where(ParkRow.energy_type.in_(energy_types)) # type:ignore
        case (False, False, True):
            stmt = stmt.where(ParkRow.name.in_(park_names)).where(ParkRow.timezone.in_(timezones)) # type:ignore
        case (False, False, False):
            stmt = (
                stmt.where(ParkRow.name.in_(park_names)) # type:ignore
                .where(ParkRow.timezone.in_(timezones)) # type:ignore
                .where(ParkRow.energy_type.in_(energy_types)) # type:ignore
            )
    return session.execute(stmt).mappings().all()


def eggs(session: Session):
    stmt = (
        select(
            ParkRow.name,
            F.min(EnergyReadingRow.megawatts).label("min"),
            F.max(EnergyReadingRow.megawatts).label("max"),
            F.sum(EnergyReadingRow.megawatts).label("sum"),
            F.count(EnergyReadingRow.megawatts).label("count"),
        )
        .join(EnergyReadingRow)
        .group_by(ParkRow.name)
    )
    return session.execute(stmt).all()


def add_dummies(session: Session):
    spongebob = ParkRow(
        name="Netterden",
        timezone="Europe/Madrid",
        energy_type="Wind",
        energy_readings=[EnergyReadingRow(megawatts=123, timestamp=datetime.now())],
    )
    sandy = ParkRow(
        name="Stadskanaal",
        timezone="Europe/Amsterdam",
        energy_type="Solar",
        energy_readings=[
            EnergyReadingRow(megawatts=-456, timestamp=datetime.now()),
            EnergyReadingRow(megawatts=789, timestamp=datetime.now()),
        ],
    )
    session.add_all([spongebob, sandy])
    session.commit()


def total(session: Session):
    stmt = (
        select(
            ParkRow.name,
            EnergyReadingRow.timestamp.cast(DATE).label("date"),
            F.min(EnergyReadingRow.megawatts).label("min"),
            F.max(EnergyReadingRow.megawatts).label("max"),
            F.sum(EnergyReadingRow.megawatts).label("sum"),
            F.count(EnergyReadingRow.megawatts).label("count"),
        )
        .join(EnergyReadingRow)
        .group_by(ParkRow.name, EnergyReadingRow.timestamp.cast(DATE))
    )
    return session.execute(stmt).all()
