def test_frontend_is_reachable(client):
    response = client.get("/")
    assert response.status_code == 200


def test_parks_returns_as_expected(client):
    response = client.get("/parks")
    assert response.status_code == 200


def test_parks_with_energy_readings_returns_as_expected(client):
    response = client.get("/parks_with_energy_readings")
    assert response.status_code == 200
