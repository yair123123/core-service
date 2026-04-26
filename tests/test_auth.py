from app.config import get_settings
from app.db.models.dispatcher_profile_model import DispatcherProfileModel
from app.db.models.driver_profile_model import DriverProfileModel
from app.db.models.station_model import StationModel
from app.db.models.user_model import UserModel
from app.db.models.user_station_model import DispatcherProfileStationModel, DriverProfileStationModel
from app.services.security import create_access_token, hash_password


def _create_user(db_session) -> UserModel:
    user = UserModel(
        username="dispatcher1",
        phone_number="0501112233",
        password_hash=hash_password("secret123"),
        is_active=True,
    )
    dispatcher_profile = DispatcherProfileModel(user=user, display_name="Dispatcher One")
    driver_profile = DriverProfileModel(
        user=user,
        display_name="Driver One",
        gender="male",
        rating=4.9,
        can_receive_rides_for_non_payment=True,
    )
    db_session.add_all([user, dispatcher_profile, driver_profile])
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
        "phoneNumber": "0501112233",
        "driverProfileId": user.driver_profile.id,
        "dispatcherProfileId": user.dispatcher_profile.id,
        "stationOwnerProfileId": None,
        "gender": "male",
        "rating": 4.9,
        "canReceiveRidesForNonPayment": True,
        "isDispatcher": True,
        "dispatcherStationsId": [],
        "driverStationsId": [],
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
            DispatcherProfileStationModel(dispatcher_profile_id=user.dispatcher_profile.id, station_id=station_1.id),
            DriverProfileStationModel(driver_profile_id=user.driver_profile.id, station_id=station_2.id),
        ]
    )
    db_session.commit()

    login_response = client.post("/auth/login", json={"username": "dispatcher1", "password": "secret123"})
    token = login_response.json()["accessToken"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["dispatcherStationsId"] == [station_1.id]
    assert response.json()["driverStationsId"] == [station_2.id]
