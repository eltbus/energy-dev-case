def test_frontend_is_responsive(client):
    response = client.get("/")
    assert response.status_code == 200


def test_parks_is_responsive(client):
    response = client.get("/parks")
    assert response.status_code == 200


def test_parks_energy_readings_is_responsive(client):
    response = client.get("/parks/energy_readings")
    assert response.status_code == 200


def test_parks_stats_is_responsive(client):
    response = client.get("/stats/parks")
    assert response.status_code == 200


def test_energy_type_stats_is_responsive(client):
    response = client.get("/stats/energy_types")
    assert response.status_code == 200
