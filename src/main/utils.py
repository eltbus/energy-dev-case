# -*-coding:utf8-*-
from typing import BinaryIO, Dict, Iterator, Union

from fastapi import UploadFile

from main.db.models import EnergyReadingRow, ParkRow


def pack(d: Dict, i: Union[ParkRow, EnergyReadingRow]):
    """
    Group by util for ParkRow and EnergyReadings to reduce response size.
    """
    energy_reading = {"megawatts": i.megawatts, "timestamp": i.timestamp}
    if d.get(i.name) is not None:
        d[i.name]["energy_readings"].append(energy_reading)
    else:
        d[i.name] = {
            "name": i.name,
            "timezone": i.timezone,
            "energy_type": i.energy_type,
            "energy_readings": [energy_reading],
        }
    return d


def genUploadFileAsString(upload_file: UploadFile, encoding: str = "utf8") -> Iterator[str]:
    binary_io: BinaryIO = upload_file.file
    for row in binary_io.readlines():
        yield row.decode(encoding)
