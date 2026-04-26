from app.config import get_settings
from app.db.models.customer_model import CustomerModel
from app.db.models.driver_profile_model import DriverProfileModel
from app.db.models.ride_model import RideModel
from app.db.models.user_model import UserModel
from app.db.models.user_station_model import DriverProfileStationModel
from app.domain.enums.ride_status import RideStatus
from app.services.security import create_access_token, hash_password


def _create_user(db_session, *, active: bool = True, driver_stations: list[int] | None = None) -> UserModel:
    user = UserModel(
        username="driver_user",
        phone_number="0502223344",
        password_hash=hash_password("secret123"),
        is_active=active,
    )
    db_session.add(user)
    db_session.flush()
    driver_profile = DriverProfileModel(
        user_id=user.id,
        display_name="Driver Test",
        gender="male",
        rating=4.9,
        can_receive_rides_for_non_payment=True,
    )
    db_session.add(driver_profile)
    db_session.flush()
    for station_id in driver_stations or []:
        db_session.add(DriverProfileStationModel(driver_profile_id=driver_profile.id, station_id=station_id))
    db_session.commit()
    db_session.refresh(user)
    return user


def _access_token_for_user(user_id: int) -> str:
    settings = get_settings()
    return create_access_token(
        user_id=user_id,
        secret_key=settings.auth_jwt_secret,
        algorithm=settings.auth_jwt_algorithm,
        expires_in_seconds=settings.auth_access_token_expires_in_seconds,
    )


def test_my_driver_rides_returns_rides_from_all_driver_stations(client, db_session):
    user = _create_user(db_session, driver_stations=[2, 5])
    customer = CustomerModel(phone_number="0521234567")
    db_session.add(customer)
    db_session.flush()

    rides = [
        RideModel(customer_id=customer.id, station_id=2, status=RideStatus.SEARCHING_DRIVER),
        RideModel(customer_id=customer.id, station_id=5, status=RideStatus.DRIVER_ASSIGNED),
        RideModel(customer_id=customer.id, station_id=8, status=RideStatus.SEARCHING_DRIVER),
        RideModel(customer_id=customer.id, station_id=2, status=RideStatus.COMPLETED),
    ]
    db_session.add_all(rides)
    db_session.commit()

    token = _access_token_for_user(user.id)
    response = client.get("/rides/my-driver-rides", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    returned = response.json()
    returned_ids = sorted(item["id"] for item in returned)
    assert returned_ids == sorted([rides[0].id, rides[1].id])
    assert all(item["station_id"] in [2, 5] for item in returned)


def test_my_driver_rides_no_driver_stations_returns_empty(client, db_session):
    user = _create_user(db_session, driver_stations=[])
    token = _access_token_for_user(user.id)

    response = client.get("/rides/my-driver-rides", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == []


def test_my_driver_rides_invalid_token_returns_401(client):
    response = client.get("/rides/my-driver-rides", headers={"Authorization": "Bearer not-a-token"})

    assert response.status_code == 401


def test_my_driver_rides_inactive_user_returns_403(client, db_session):
    user = _create_user(db_session, active=False, driver_stations=[2])
    token = _access_token_for_user(user.id)

    response = client.get("/rides/my-driver-rides", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
