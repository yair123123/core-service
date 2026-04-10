from app.config import get_settings
from app.db.models.station_model import StationModel
from app.db.models.user_model import UserModel
from app.db.models.user_station_model import UserDispatcherStationModel, UserDriverStationModel
from app.services.security import create_access_token, hash_password


def _create_user(db_session) -> UserModel:
    user = UserModel(
        username="dispatcher1",
        password_hash=hash_password("secret123"),
        is_active=True,
        gender="male",
        rating=4.9,
        can_receive_rides_for_non_payment=True,
        is_dispatcher=True,
        dispatcher_stations_id=[1, 2],
        driver_stations_id=[7],
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success(client, db_session):
    _create_user(db_session)

    response = client.post("/auth/login", json={"username": "dispatcher1", "password": "secret123"})
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["accessToken"], str)
    assert body["refreshToken"] is None
    assert body["expiresIn"] == get_settings().auth_access_token_expires_in_seconds


def test_login_failed_invalid_credentials(client, db_session):
    _create_user(db_session)

    response = client.post("/auth/login", json={"username": "dispatcher1", "password": "bad-pass"})
    assert response.status_code == 401


def test_auth_me_success(client, db_session):
    user = _create_user(db_session)
    login_response = client.post("/auth/login", json={"username": "dispatcher1", "password": "secret123"})
    token = login_response.json()["accessToken"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "username": "dispatcher1",
        "gender": "male",
        "rating": 4.9,
        "canReceiveRidesForNonPayment": True,
        "isDispatcher": True,
        "dispatcherStationsId": [1, 2],
        "driverStationsId": [7],
    }


def test_auth_me_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401


def test_auth_me_expired_token(client, db_session):
    user = _create_user(db_session)
    settings = get_settings()
    expired_token = create_access_token(
        user_id=user.id,
        secret_key=settings.auth_jwt_secret,
        algorithm=settings.auth_jwt_algorithm,
        expires_in_seconds=-60,
    )

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_auth_me_prefers_foreign_key_station_links(client, db_session):
    user = _create_user(db_session)
    station_1 = StationModel(name="Tel Aviv", is_active=True)
    station_2 = StationModel(name="Haifa", is_active=True)
    db_session.add_all([station_1, station_2])
    db_session.flush()
    db_session.add_all(
        [
            UserDispatcherStationModel(user_id=user.id, station_id=station_1.id),
            UserDriverStationModel(user_id=user.id, station_id=station_2.id),
        ]
    )
    db_session.commit()

    login_response = client.post("/auth/login", json={"username": "dispatcher1", "password": "secret123"})
    token = login_response.json()["accessToken"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["dispatcherStationsId"] == [station_1.id]
    assert response.json()["driverStationsId"] == [station_2.id]
