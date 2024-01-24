from datetime import date, datetime
from typing import List, NamedTuple, Optional, Sequence

from sqlalchemy import func as F
from sqlalchemy import select
from sqlalchemy.engine import RowMapping
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Select
from sqlalchemy.types import DATE

from main.constraints import EnergyType, ParkName, Timezone
from main.db.models import EnergyReadingRow, ParkRow


class ParkEnergyReadingsRow(NamedTuple):
    name: str
    timezone: str
    energy_type: str
    megawatts: float
    timestamp: datetime


def add_park_and_energy_readings_where_condition(
    stmt: Select,
    park_names: List[ParkName] = [],
    timezones: List[Timezone] = [],
    energy_types: List[EnergyType] = [],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Select:
    """
    Compound select statatement with where conditions
    """
    if park_names:
        stmt = stmt.where(ParkRow.name.in_(park_names))
    if timezones:
        stmt = stmt.where(ParkRow.timezone.in_(timezones))
    if energy_types:
        stmt = stmt.where(ParkRow.energy_type.in_(energy_types))
    if start_date and end_date:
        stmt = stmt.where(EnergyReadingRow.timestamp.between(start_date, end_date))
    elif start_date:
        stmt = stmt.where(EnergyReadingRow.timestamp > start_date)
    elif end_date:
        stmt = stmt.where(EnergyReadingRow.timestamp < end_date)
    return stmt


def select_parks(
    session: Session, timezones: List[Timezone], energy_types: List[EnergyType], offset: int, limit: int
) -> Sequence[RowMapping]:
    stmt = select(ParkRow.name, ParkRow.timezone, ParkRow.energy_type).offset(offset).limit(limit)
    if timezones:
        stmt = stmt.where(ParkRow.timezone.in_(timezones))
    if energy_types:
        stmt = stmt.where(ParkRow.energy_type.in_(energy_types))
    return session.execute(stmt).mappings().all()


def select_parks_with_energy_readings(
    session: Session,
    offset: int,
    limit: int,
    park_names: List[ParkName] = [],
    timezones: List[Timezone] = [],
    energy_types: List[EnergyType] = [],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Sequence[ParkEnergyReadingsRow]:
    stmt = (
        select(
            ParkRow.name, ParkRow.timezone, ParkRow.energy_type, EnergyReadingRow.megawatts, EnergyReadingRow.timestamp
        )
        .offset(offset)
        .limit(limit)
        .join(EnergyReadingRow)
    )
    stmt = add_park_and_energy_readings_where_condition(
        stmt=stmt,
        park_names=park_names,
        timezones=timezones,
        energy_types=energy_types,
        start_date=start_date,
        end_date=end_date,
    )
    results = session.execute(stmt).mappings().all()
    return [ParkEnergyReadingsRow(**row) for row in results]


def select_stats_by_park_and_date(
    session: Session,
    offset: int,
    limit: int,
    park_names: List[ParkName] = [],
    timezones: List[Timezone] = [],
    energy_types: List[EnergyType] = [],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Sequence[RowMapping]:
    stmt = (
        select(
            ParkRow.name,
            EnergyReadingRow.timestamp.cast(DATE).label("date"),
            F.min(EnergyReadingRow.megawatts).label("min"),
            F.max(EnergyReadingRow.megawatts).label("max"),
            F.sum(EnergyReadingRow.megawatts).label("sum"),
            F.count(EnergyReadingRow.megawatts).label("count"),
        )
        .offset(offset)
        .limit(limit)
        .join(EnergyReadingRow)
    )
    stmt = add_park_and_energy_readings_where_condition(
        stmt=stmt,
        park_names=park_names,
        timezones=timezones,
        energy_types=energy_types,
        start_date=start_date,
        end_date=end_date,
    )
    stmt = stmt.group_by(ParkRow.name, EnergyReadingRow.timestamp.cast(DATE))
    stmt = stmt.order_by(EnergyReadingRow.timestamp.cast(DATE))
    return session.execute(stmt).mappings().all()


def select_stats_by_energy_type_and_date(
    session: Session,
    offset: int,
    limit: int,
    park_names: List[ParkName] = [],
    timezones: List[Timezone] = [],
    energy_types: List[EnergyType] = [],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Sequence[RowMapping]:
    stmt = (
        select(
            ParkRow.energy_type,
            EnergyReadingRow.timestamp.cast(DATE).label("date"),
            F.min(EnergyReadingRow.megawatts).label("min"),
            F.max(EnergyReadingRow.megawatts).label("max"),
            F.sum(EnergyReadingRow.megawatts).label("sum"),
            F.count(EnergyReadingRow.megawatts).label("count"),
        )
        .offset(offset)
        .limit(limit)
        .join(EnergyReadingRow)
    )
    stmt = add_park_and_energy_readings_where_condition(
        stmt=stmt,
        park_names=park_names,
        timezones=timezones,
        energy_types=energy_types,
        start_date=start_date,
        end_date=end_date,
    )
    stmt = stmt.group_by(ParkRow.energy_type, EnergyReadingRow.timestamp.cast(DATE))
    stmt = stmt.order_by(EnergyReadingRow.timestamp.cast(DATE))
    return session.execute(stmt).mappings().all()
