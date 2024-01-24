"""
Since we're using PostgreSQL as our Database, only integration tests can be done.
"""
from functools import reduce

from main.constraints import EnergyType, ParkName, Timezone
from main.db.queries import select_parks_with_energy_readings
from main.utils import pack


def test_select_parks_returns_expected(session):
    park_names = [ParkName.netterden, ParkName.stadskanaal]
    timezones = [Timezone.amsterdam, Timezone.bucharest]
    energy_types = [EnergyType.wind, EnergyType.solar]
    park_names = [ParkName.netterden, ParkName.stadskanaal]
    rows = select_parks_with_energy_readings(
        session, park_names=park_names, timezones=timezones, energy_types=energy_types, offset=0, limit=10
    )
    result = reduce(pack, rows, {})  # type:ignore
    for i in result:
        print(i)
    assert len(list(result.values())) == 2
