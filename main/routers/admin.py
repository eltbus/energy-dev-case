# -*-coding:utf8-*-
from csv import DictReader
from datetime import date, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Query, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.status import (
    HTTP_200_OK,
)

from main.constraints import ParkName
from main.db import get_session
from main.db.models import EnergyReadingRow, MeasurementRow, ParkRow, StationRow
from main.utils import gen_upload_file_as_string
from main.routers.exceptions import handle_upsert

router = APIRouter(prefix="/admin", tags=["ADMIN"])


@router.post("/parks/upload")
async def insert_parks_from_file(
    *,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    upload_file: UploadFile,
) -> JSONResponse:
    """
    Insert parks into the database from an uploaded CSV file.

    The CSV file must have the following columns:
    park_name: The unique name of the park.
    timezone: The timezone in which the park is located.
    energy_type: The type of energy produced by the park (e.g., Wind, Solar).

    Args:
        background_tasks: FastAPI's BackgroundTasks instance for managing background tasks.
        session: The database session.
        upload_file: The uploaded CSV file.

    Returns:
        A JSON response with the number of rows successfully inserted/updated.

    Example file:
        park_name,timezone,energy_type
        Netterden,Europe/Amsterdam,Wind
        Stadskanaal,Europe/Bucharest,Solar
    """
    n = 0
    try:
        f = gen_upload_file_as_string(upload_file.file)
        with handle_upsert():
            for n, row in enumerate(DictReader(f, delimiter=","), start=1):
                session.add(
                    ParkRow(
                        name=row["park_name"],
                        timezone=row["timezone"],
                        energy_type=row["energy_type"],
                    )
                )
            session.commit()
    finally:
        background_tasks.add_task(upload_file.file.close)

    content = {"message": f"{n} rows successfully inserted/updated"}
    return JSONResponse(content, status_code=HTTP_200_OK)


@router.post("/energy-readings/upload")
async def insert_energy_readings_from_file(
    *,
    background_tasks: BackgroundTasks,
    park_name: ParkName = Query(..., description="Park to associate this readings to."),
    session: Session = Depends(get_session),
    upload_file: UploadFile,
):
    """
    Insert energy readings for a given park into the database from an uploaded CSV file.

    The CSV file must have the following columns:
    datetime: The timestamp of the energy reading (ISO 8601 format).
    MW: The energy production in megawatts at the given timestamp.

    Args:
        background_tasks: FastAPI's BackgroundTasks instance for managing background tasks.
        park_name: The name of the park to associate the energy readings with.
        session: The database session.
        upload_file: The uploaded CSV file.

    Returns:
        A JSON response with the number of rows successfully inserted/updated.

    Example file:
        datetime,MW
        2020-03-01 00:00:00,10.108
        2020-03-01 00:15:00,11.196
    """
    n = 0
    try:
        f = gen_upload_file_as_string(upload_file.file)
        with handle_upsert():
            for n, row in enumerate(DictReader(f, delimiter=","), start=1):
                session.add(
                    EnergyReadingRow(
                        park_name=park_name,
                        timestamp=datetime.fromisoformat(row["datetime"]),
                        megawatts=row["MW"],
                    )
                )
            session.commit()
    finally:
        background_tasks.add_task(upload_file.file.close)

    content = {"message": f"{n} rows successfully inserted/updated"}
    return JSONResponse(content, status_code=HTTP_200_OK)


@router.post("/stations/upload")
async def insert_stations_from_file(
    *,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    upload_file: UploadFile,
):
    """
    Insert parks into the database from an uploaded CSV file.

    The CSV file must have the following columns:
    park_name: The unique name of the park.
    timezone: The timezone in which the park is located.
    energy_type: The type of energy produced by the park (e.g., Wind, Solar).

    Args:
        background_tasks: FastAPI's BackgroundTasks instance for managing background tasks.
        session: The database session.
        upload_file: The uploaded CSV file.

    Returns:
        A JSON response with the number of rows successfully inserted/updated.

    Example file:
        park_name,timezone,energy_type
        Netterden,Europe/Amsterdam,Wind
        Stadskanaal,Europe/Bucharest,Solar
    """
    n = 0
    try:
        f = gen_upload_file_as_string(upload_file.file)
        with handle_upsert():
            for n, row in enumerate(DictReader(f, delimiter=","), start=1):
                session.add(
                    ParkRow(
                        name=row["park_name"],
                        timezone=row["timezone"],
                        energy_type=row["energy_type"],
                    )
                )
            session.commit()
    finally:
        background_tasks.add_task(upload_file.file.close)

    content = {"message": f"{n} rows successfully inserted/updated"}
    return JSONResponse(content, status_code=HTTP_200_OK)


@router.post("/measurements/upload")
async def insert_measurements_from_file(
    *,
    background_tasks: BackgroundTasks,
    station_code: str = Query(..., description="Station to associate this measurements to."),
    session: Session = Depends(get_session),
    upload_file: UploadFile,
) -> JSONResponse:
    """
    Insert measurements for a given station into the database from an uploaded CSV file.

    The CSV file must have the following columns:
    datetime: The timestamp of the energy reading (ISO 8601 format).
    MW: The energy production in megawatts at the given timestamp.

    Args:
        background_tasks: FastAPI's BackgroundTasks instance for managing background tasks.
        station_code: The code of the station to associate the measurements with.
        session: The database session.
        upload_file: The uploaded CSV file.

    Returns:
        A JSON response with the number of rows successfully inserted/updated.

    Example file:
        FECHA;INDICATIVO;NOMBRE;PROVINCIA;ALTITUD;TMEDIA;PRECIPITACION;TMIN;HORATMIN;TMAX;HORATMAX;DIR;VELMEDIA;RACHA;HORARACHA;SOL;PRESMAX;HORAPRESMAX;PRESMIN;HORAPRESMIN
        1968-03-01;0002I;VANDELLÒS;TARRAGONA;32;8.9;21.0;6.6;03:00;11.2;18:00;05;1.9;6.7;10:55;0.0;;;;
    """
    n = 0
    try:
        f = gen_upload_file_as_string(upload_file.file)
        with handle_upsert():
            for n, row in enumerate(DictReader(f, delimiter=","), start=1):
                stmt = select(StationRow.id).where(StationRow.code == station_code)
                station_id = session.execute(stmt).one()
                session.add(
                    MeasurementRow(
                        station_id=station_id,
                        date=date.fromisoformat(row["FECHA"]),
                        avg_temp=row["TMEDIA"],
                        min_temp=row["TMIN"],
                        max_temp=row["TMAX"],
                    )
                )
            session.commit()
    finally:
        background_tasks.add_task(upload_file.file.close)

    content = {"message": f"{n} rows successfully inserted/updated"}
    return JSONResponse(content, status_code=HTTP_200_OK)
