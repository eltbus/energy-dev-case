from functools import reduce
from typing import List, Dict

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from main.constraints import EnergyType, ParkName, Timezone
from main.db import getSession
from main.db.queries import (eggs, selectParks, selectParksWithEnergyReadings, total)
from main.utils import pack

router = APIRouter()


@router.get("/")
def read_root():
    return RedirectResponse("docs")


@router.get("/parks")
def read_parks(
    session: Session = Depends(getSession),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return selectParks(session=session, timezones=timezones, energy_types=energy_types, offset=offset, limit=limit)


@router.get("/parks_with_energy_readings")
def read_parks_with_energy_readings(
    session: Session = Depends(getSession),
    park_names: List[ParkName] = Query(default=[]),
    energy_types: List[EnergyType] = Query(default=[]),
    timezones: List[Timezone] = Query(default=[]),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    rows = selectParksWithEnergyReadings(
        session, park_names=park_names, timezones=timezones, energy_types=energy_types, offset=offset, limit=limit
    )
    packed_rows: Dict = reduce(pack, rows, {})  # type:ignore
    return [packed_rows[key] for key in packed_rows]


@router.get("/stats")
def read_stats(session: Session = Depends(getSession)):
    return eggs(session)


@router.get("/production")
def agg_total_production_by_date(session: Session = Depends(getSession)):
    return total(session)
