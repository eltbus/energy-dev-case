# -*-coding:utf8-*-
from typing import BinaryIO, Dict, Iterator

from main.db.queries import ParkEnergyReadingsRow


def pack(d: Dict, i: ParkEnergyReadingsRow) -> Dict:
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


def gen_upload_file_as_string(binary_io: BinaryIO, encoding: str = "utf8") -> Iterator[str]:
    """
    Yield lines for storage
    """
    for line in binary_io.readlines():
        yield line.decode(encoding)
