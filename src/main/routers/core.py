from datetime import date
from functools import reduce
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from main.constraints import EnergyType, ParkName, Timezone
from main.db import getSession
from main.db.queries import (selectParks, selectParksWithEnergyReadings,
                             selectStatsByEnergyTypeAndDate,
                             selectStatsByParkAndDate)
from main.models import EnergyTypeStats, Park, ParkStats
from main.utils import pack

router = APIRouter()


@router.get("/")
def redirect_to_docs():
    """
    Redirect to low effort frontend -> OpenAPI
    """
    return RedirectResponse("docs")


@router.get("/parks", response_model=List[Park], response_model_exclude_none=True)
def read_parks(
    session: Session = Depends(getSession),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    """
    Get parks in database
    """
    return selectParks(session=session, timezones=timezones, energy_types=energy_types, offset=offset, limit=limit)


@router.get("/parks/energy_readings", response_model=List[Park])
def read_parks_with_energy_readings(
    session: Session = Depends(getSession),
    park_names: List[ParkName] = Query(default=[]),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    """
    Get park energy production readings.
    """
    rows = selectParksWithEnergyReadings(
        session,
        park_names=park_names,
        timezones=timezones,
        energy_types=energy_types,
        offset=offset,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
    packed_rows: Dict = reduce(pack, rows, {})  # type:ignore
    return [packed_rows[key] for key in packed_rows]


@router.get("/stats/parks", response_model=List[ParkStats])
def read_park_stats(
    session: Session = Depends(getSession),
    park_names: List[ParkName] = Query(default=[]),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    """
    Get park stats
    """
    return selectStatsByParkAndDate(
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
    session: Session = Depends(getSession),
    park_names: List[ParkName] = Query(default=[]),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    """
    Get energy_type stats
    """
    return selectStatsByEnergyTypeAndDate(
        session,
        park_names=park_names,
        energy_types=energy_types,
        timezones=timezones,
        offset=offset,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
