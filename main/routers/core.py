from datetime import date
from functools import reduce
from typing import Dict, List, Optional, Sequence

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.engine.row import RowMapping

from main.constraints import EnergyType, ParkName, Timezone
from main.db import get_session
from main.db.queries import (
    select_parks,
    select_parks_with_energy_readings,
    select_stats_by_energy_type_and_date,
    select_stats_by_park_and_date,
)
from main.models import EnergyTypeStats, Park, ParkStats
from main.utils import pack

router = APIRouter()


@router.head("/")
@router.get("/")
def redirect_to_docs() -> RedirectResponse:
    """
    Redirect to low effort frontend -> OpenAPI
    """
    return RedirectResponse("docs")


@router.get("/parks", response_model=List[Park], response_model_exclude_none=True)
def read_parks(
    session: Session = Depends(get_session),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> Sequence[RowMapping]:
    """
    Get parks in database
    """
    return select_parks(session=session, timezones=timezones, energy_types=energy_types, offset=offset, limit=limit)


@router.get("/parks/energy-readings", response_model=List[Park])
def read_parks_with_energy_readings(
    session: Session = Depends(get_session),
    park_names: List[ParkName] = Query(default=[]),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> Sequence[RowMapping]:
    """
    Get park energy production readings.
    """
    rows = select_parks_with_energy_readings(
        session,
        park_names=park_names,
        timezones=timezones,
        energy_types=energy_types,
        offset=offset,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
    packed_rows: Dict = reduce(pack, rows, {})
    return [packed_rows[key] for key in packed_rows]


@router.get("/stats/parks", response_model=List[ParkStats])
def read_park_stats(
    session: Session = Depends(get_session),
    park_names: List[ParkName] = Query(default=[]),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> Sequence[RowMapping]:
    """
    Get park stats
    """
    return select_stats_by_park_and_date(
        session,
        park_names=park_names,
        energy_types=energy_types,
        timezones=timezones,
        offset=offset,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/stats/energy_types", response_model=List[EnergyTypeStats])
def read_energy_type_stats(
    session: Session = Depends(get_session),
    park_names: List[ParkName] = Query(default=[]),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
) -> Sequence[RowMapping]:
    """
    Get energy_type stats
    """
    return select_stats_by_energy_type_and_date(
        session,
        park_names=park_names,
        energy_types=energy_types,
        timezones=timezones,
        offset=offset,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
