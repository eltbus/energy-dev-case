import os
from datetime import date, datetime
from typing import List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.routing import Route
from testcontainers.postgres import PostgresContainer

from main import start_api
from main.constraints import EnergyType, ParkName, Timezone
from main.db import get_session
from main.db.models import (Base, EnergyReadingRow, MeasurementRow, ParkRow,
                            StationRow)

api = start_api()
client = TestClient(api)

from logging import getLogger

LOGGER = getLogger(__name__)


@pytest.fixture(scope="session")
def park_data() -> List[ParkRow]:
    """
    Dummy data
    """
    return [
        ParkRow(
            name=ParkName.netterden,
            timezone=Timezone.amsterdam,
            energy_type=EnergyType.wind,
            energy_readings=[EnergyReadingRow(megawatts=123, timestamp=datetime.now())],
        ),
        ParkRow(
            name=ParkName.stadskanaal,
            timezone=Timezone.bucharest,
            energy_type=EnergyType.solar,
            energy_readings=[
                EnergyReadingRow(megawatts=-456, timestamp=datetime.now()),
                EnergyReadingRow(megawatts=789, timestamp=datetime.now()),
            ],
        ),
    ]


@pytest.fixture(scope="session")
def stations_data() -> List[StationRow]:
    """
    Dummy data
    """
    return [
        StationRow(
            code="0000",
            name="0000",
            province="foo",
            latitude="foo",
            longitude="foo",
            altitude="foo",
            measurements=[MeasurementRow(date=date(1993, 7, 22), avg_temp=20, min_temp=0, max_temp=25)],
        ),
        StationRow(
            code="0001",
            name="0001",
            province="foo",
            latitude="foo",
            longitude="foo",
            altitude="foo",
            measurements=[MeasurementRow(date=date.today(), avg_temp=20, min_temp=0, max_temp=25)],
        ),
    ]


@pytest.fixture(scope="session")  # Re-use scope to speed up tests
def session(park_data: List[ParkRow], stations_data: List[StationRow]):
    """
    Start containerized database -> engine -> add dummy data -> and yield session
    """
    with PostgresContainer(
        user=os.environ.get("POSTGRES_USER", "test"),
        password=os.environ.get("POSTGRES_PASSWORD", "test"),
        dbname=os.environ.get("POSTGRES_DB", "test"),
        driver="psycopg2",
    ) as postgres:
        engine = create_engine(postgres.get_connection_url(), future=True)

        # Create modeled tables
        Base.metadata.create_all(engine)

        # Initialize some rows
        with Session(engine, future=True) as session:
            session.add_all(park_data)
            session.add_all(stations_data)
            session.commit()
            yield session


@pytest.fixture(name="api")
def api_fixture() -> FastAPI:
    return start_api()


@pytest.fixture(name="routes")
def routes_fixture() -> List[str]:
    from main.routers.core import router as core_router

    return [route.path for route in core_router.routes if isinstance(route, Route)]


@pytest.fixture(name="client")
def client_fixture(session: Session, api):
    api.dependency_overrides[get_session] = lambda: session
    client = TestClient(api)
    yield client
    api.dependency_overrides.clear()
