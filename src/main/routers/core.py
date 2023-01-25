from functools import reduce
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from main.constraints import EnergyType, ParkName, Timezone
from main.db import getSession
from main.db.queries import (add_dummies, eggs, selectParks,
                             selectParksWithEnergyReadings)
from main.utils import pack

router = APIRouter()


@router.get("/")
def read_root():
    return RedirectResponse("docs")


@router.get("/parks")
def read_parks(
    session: Session = Depends(getSession),
    energy_types: List[EnergyType] = Query(None),
    timezones: List[Timezone] = Query(None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    return selectParks(session=session, timezones=timezones, energy_types=energy_types, offset=offset, limit=limit)


@router.get("/parks_with_energy_readings")
def read_parks_with_energy_readings(
    session: Session = Depends(getSession),
    park_names: List[ParkName] = Query(None),
    energy_types: List[EnergyType] = Query(None),
    timezones: List[Timezone] = Query(None),
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
):
    rows = selectParksWithEnergyReadings(
        session, park_names=park_names, timezones=timezones, energy_types=energy_types, offset=offset, limit=limit
    )
    return reduce(pack, rows, {})  # type:ignore


@router.get("/stats")
def read_stats(session: Session = Depends(getSession)):
    return eggs(session)


@router.get("/dummy")
def dummy_data(session: Session = Depends(getSession)):
    add_dummies(session)
    return "OK"
