# -*-coding:utf8-*-
from csv import DictReader
from datetime import datetime

from fastapi import APIRouter, Depends, Query, UploadFile
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

# Utils
@router.post("/upload_parks", tags=["ADMIN"])
async def insert_parks_from_file(*, session: Session = Depends(get_session), upload_file: UploadFile):
    """
    Insert parks into database.
    Example file:
        park_name,timezone,energy_type
        Netterden,Europe/Amsterdam,Wind
        Stadskanaal,Europe/Bucharest,Solar
    """
    n = 0
    try:
        f = gen_upload_file_as_string(upload_file)
        for n, row in enumerate(DictReader(f, delimiter=","), start=1):
            session.add(
                ParkRow(
                    name=row["park_name"],
                    timezone=row["timezone"],
                    energy_type=row["energy_type"],
                )
            )
        session.commit()
    except KeyError as e:
        status_code = HTTP_400_BAD_REQUEST
        content = {"error": f"Invalid row format. Upload aborted."}
    except IntegrityError as e:
        status_code = HTTP_409_CONFLICT
        content = {"error": repr(e)}
    except Exception as e:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        content = {"error": "There was an error uploading the file"}
    else:
        status_code = HTTP_200_OK
        content = {"message": f"{n} rows successfully inserted/updated"}
    finally:
        await upload_file.close()
    return JSONResponse(content, status_code=status_code)


@router.post("/upload_energy_readings", tags=["ADMIN"])
async def insert_energy_readings_from_file(
    *,
    park_name: ParkName = Query(..., description="Park to associate this readings to."),
    session: Session = Depends(get_session),
    upload_file: UploadFile,
):
    """
    Insert energy readings for a given park into database.
    Example file:
        datetime,MW
        2020-03-01 00:00:00,10.108
        2020-03-01 00:15:00,11.196
    """
    n = 0
    try:
        f = gen_upload_file_as_string(upload_file)
        for n, row in enumerate(DictReader(f, delimiter=","), start=1):
            session.add(
                EnergyReadingRow(
                    park_name=park_name,
                    timestamp=datetime.fromisoformat(row["datetime"]),
                    megawatts=row["MW"],
                )
            )
        session.commit()
    except KeyError as e:
        status_code = HTTP_400_BAD_REQUEST
        content = {"error": f"Invalid row format. Upload aborted.\n{repr(e)}"}
    except IntegrityError as e:
        status_code = HTTP_409_CONFLICT
        content = {"error": repr(e)}
    except Exception as e:
        status_code = HTTP_500_INTERNAL_SERVER_ERROR
        print(repr(e))
        content = {"error": "There was an error uploading the file"}
    else:
        status_code = HTTP_200_OK
        content = {"message": f"{n} rows successfully inserted/updated"}
    finally:
        await upload_file.close()
    return JSONResponse(content, status_code=status_code)
