from datetime import date
from typing import List, Optional, Sequence

from sqlalchemy import func as F
from sqlalchemy import select
from sqlalchemy.engine import RowMapping
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Select
from sqlalchemy.types import DATE

from main.constraints import EnergyType, ParkName, Timezone
from main.db.models import EnergyReadingRow, ParkRow


def addParkAndEnergyReadingsWhereCondition(
    stmt: Select,
    park_names: List[ParkName] = [],
    timezones: List[Timezone] = [],
    energy_types: List[EnergyType] = [],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    if park_names:
        stmt = stmt.where(ParkRow.name.in_(park_names))  # type:ignore
    if timezones:
        stmt = stmt.where(ParkRow.timezone.in_(timezones))  # type:ignore
    if energy_types:
        stmt = stmt.where(ParkRow.energy_type.in_(energy_types))  # type:ignore
    if start_date and end_date:
        stmt = stmt.where(EnergyReadingRow.timestamp.between(start_date, end_date))  # type:ignore
    elif start_date:
        stmt = stmt.where(EnergyReadingRow.timestamp > start_date)  # type:ignore
    elif end_date:
        stmt = stmt.where(EnergyReadingRow.timestamp < end_date)  # type:ignore
    return stmt


def selectParks(
    session: Session, timezones: List[Timezone], energy_types: List[EnergyType], offset: int, limit: int
) -> Sequence[RowMapping]:
    stmt = select(ParkRow.name, ParkRow.timezone, ParkRow.energy_type).offset(offset).limit(limit)
    match (not timezones, not energy_types):
        case (True, True):
            pass
        case (True, False):
            stmt = stmt.where(ParkRow.energy_type.in_(energy_types))  # type:ignore
        case (False, True):
            stmt = stmt.where(ParkRow.timezone.in_(timezones))  # type:ignore
        case (False, False):
            stmt = stmt.where(ParkRow.timezone.in_(timezones)).where(
                ParkRow.energy_type.in_(energy_types)
            )  # type:ignore
    return session.execute(stmt).mappings().all()


def selectParksWithEnergyReadings(
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
            ParkRow.name, ParkRow.timezone, ParkRow.energy_type, EnergyReadingRow.megawatts, EnergyReadingRow.timestamp
        )
        .offset(offset)
        .limit(limit)
        .join(EnergyReadingRow)
    )
    stmt = addParkAndEnergyReadingsWhereCondition(
        stmt=stmt,
        park_names=park_names,
        timezones=timezones,
        energy_types=energy_types,
        start_date=start_date,
        end_date=end_date,
    )
    return session.execute(stmt).mappings().all()


def selectStatsByParkAndDate(
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
    stmt = addParkAndEnergyReadingsWhereCondition(
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


def selectStatsByEnergyTypeAndDate(
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
    stmt = addParkAndEnergyReadingsWhereCondition(
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
