# -*-coding:utf8-*-
from contextlib import contextmanager
from csv import DictReader
from datetime import datetime

from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Query,
                     UploadFile)
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                              HTTP_409_CONFLICT,
                              HTTP_500_INTERNAL_SERVER_ERROR)

from main.constraints import ParkName
from main.db import get_session
from main.db.models import EnergyReadingRow, ParkRow
from main.utils import gen_upload_file_as_string

router = APIRouter(prefix="/admin")


@contextmanager
def handle_upsert():
    """
    A context manager for handling exceptions during the upsert operation.

    Raises:
        HTTPException: For various error scenarios:
            - HTTP_400_BAD_REQUEST for an invalid row format.
            - HTTP_409_CONFLICT for integrity errors during upsert.
            - HTTP_500_INTERNAL_SERVER_ERROR for other exceptions.
    """
    try:
        yield
    except KeyError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid row format. Upload aborted.")
    except IntegrityError as e:
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail=repr(e))
    except Exception:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="There was an error uploading the file")


@router.post("/parks/upload", tags=["ADMIN"])
async def insert_parks_from_file(
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


@router.post("/energy-readings/upload", tags=["ADMIN"])
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
