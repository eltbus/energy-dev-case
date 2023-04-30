from tempfile import SpooledTemporaryFile

import pytest
from fastapi.testclient import TestClient

from main.constraints import ParkName


def test_frontend_is_responsive(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200


def test_parks_is_responsive(client: TestClient):
    response = client.get("/parks")
    assert response.status_code == 200


def test_parks_energy_readings_is_responsive(client: TestClient):
    response = client.get("/parks/energy_readings")
    assert response.status_code == 200


def test_parks_stats_is_responsive(client: TestClient):
    response = client.get("/stats/parks")
    assert response.status_code == 200


def test_energy_type_stats_is_responsive(client: TestClient):
    response = client.get("/stats/energy_types")
    assert response.status_code == 200


@pytest.fixture(scope="session")
def empty_file():
    with SpooledTemporaryFile() as w:
        w.seek(0)
        yield w


@pytest.fixture(scope="session")
def dummy_park_file():
    with SpooledTemporaryFile() as w:
        header = "park_name,timezone,energy_type\n"
        data = "Zwartenbergseweg,Europe/Volgograd,Wind"
        w.write(header.encode())
        w.write(data.encode())
        w.seek(0)
        yield w


@pytest.fixture(scope="session")
def dummy_energy_readings_file():
    with SpooledTemporaryFile() as w:
        header = "datetime,MW\n"
        data = "2020-03-01 00:00:00,10.108"
        w.write(header.encode())
        w.write(data.encode())
        w.seek(0)
        yield w


def test_upload_wrong_filename_returns_error_response(client: TestClient, dummy_park_file, dummy_energy_readings_file):
    response = client.post("/admin/upload_parks", files=[("hola", dummy_park_file)])
    assert response.is_error
    assert response.is_client_error
    assert (
        response.text
        == '{"detail":[{"loc":["body","upload_file"],"msg":"field required","type":"value_error.missing"}]}'
    )

    response = client.post(
        "/admin/upload_energy_readings",
        params={"park_name": ParkName.netterden.value},
        files=[("hola", dummy_energy_readings_file)],
    )
    assert response.is_error
    assert response.is_client_error
    assert (
        response.text
        == '{"detail":[{"loc":["body","upload_file"],"msg":"field required","type":"value_error.missing"}]}'
    )


def test_empty_file_upserts_no_park_rows(client: TestClient, empty_file):
    response = client.post("/admin/upload_parks", files=[("upload_file", empty_file)])
    assert response.is_success
    assert response.text == '{"message":"0 rows successfully inserted/updated"}'


def test_empty_file_upserts_no_energy_reading_rows(client: TestClient, empty_file):
    response = client.post(
        "/admin/upload_energy_readings",
        params={"park_name": ParkName.netterden.value},
        files=[("upload_file", empty_file)],
    )
    assert response.is_success
    assert response.text == '{"message":"0 rows successfully inserted/updated"}'


def test_dummy_park_data(client: TestClient, dummy_park_file):
    response = client.post("/admin/upload_parks", files=[("upload_file", dummy_park_file)])
    assert response.is_success
    assert response.text == '{"message":"1 rows successfully inserted/updated"}'


def test_dummy_energy_readings_data(client: TestClient, dummy_energy_readings_file):
    response = client.post(
        "/admin/upload_energy_readings",
        params={"park_name": ParkName.netterden.value},
        files=[("upload_file", dummy_energy_readings_file)],
    )
    assert response.is_success
    assert response.text == '{"message":"1 rows successfully inserted/updated"}'
