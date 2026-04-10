from app.db.models.station_model import StationModel


def test_get_all_stations_returns_active_only(client, db_session):
    db_session.add_all(
        [
            StationModel(name="Tel Aviv", is_active=True),
            StationModel(name="Haifa", is_active=True),
            StationModel(name="Old Station", is_active=False),
        ]
    )
    db_session.commit()

    response = client.get("/stations")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Tel Aviv", "isActive": True},
        {"id": 2, "name": "Haifa", "isActive": True},
    ]


def test_get_station_by_id_success(client, db_session):
    station = StationModel(name="Jerusalem", is_active=True)
    db_session.add(station)
    db_session.commit()

    response = client.get(f"/stations/{station.id}")
    assert response.status_code == 200
    assert response.json() == {"id": station.id, "name": "Jerusalem", "isActive": True}


def test_get_station_by_id_not_found(client):
    response = client.get("/stations/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Station not found"


def test_get_stations_by_ids_success(client, db_session):
    db_session.add_all(
        [
            StationModel(name="Tel Aviv", is_active=True),
            StationModel(name="Haifa", is_active=True),
            StationModel(name="Disabled", is_active=False),
        ]
    )
    db_session.commit()

    response = client.post("/stations/by-ids", json={"ids": [1, 2, 3]})
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "name": "Tel Aviv", "isActive": True},
        {"id": 2, "name": "Haifa", "isActive": True},
    ]


def test_get_stations_by_ids_empty_list(client):
    response = client.post("/stations/by-ids", json={"ids": []})
    assert response.status_code == 200
    assert response.json() == []


def test_get_stations_by_ids_partially_invalid(client, db_session):
    station = StationModel(name="Tel Aviv", is_active=True)
    db_session.add(station)
    db_session.commit()

    response = client.post("/stations/by-ids", json={"ids": [station.id, 99999]})
    assert response.status_code == 200
    assert response.json() == [{"id": station.id, "name": "Tel Aviv", "isActive": True}]
