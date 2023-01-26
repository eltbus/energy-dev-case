import os
from datetime import datetime
from typing import List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from main import start_api
from main.constraints import EnergyType, ParkName, Timezone
from main.db import get_session
from main.db.models import Base, EnergyReadingRow, ParkRow

api = start_api()
client = TestClient(api)


@pytest.fixture(scope="session")
def data() -> List[ParkRow]:
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


@pytest.fixture(scope="session")  # Re-use scope to speed up tests
def session(data: List[ParkRow]):
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
            session.add_all(data)
            session.commit()
            yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    api = start_api()
    api.dependency_overrides[get_session] = lambda: session
    client = TestClient(api)
    yield client
    api.dependency_overrides.clear()
