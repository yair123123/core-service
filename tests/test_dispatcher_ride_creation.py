import json

from app.config import get_settings
from app.db.models.customer_model import CustomerModel
from app.db.models.ride_event_model import RideEventModel
from app.db.models.ride_model import RideModel
from app.db.models.user_model import UserModel
from app.domain.enums.ride_status import RideStatus
from app.services.security import create_access_token, hash_password


def _create_user(db_session, *, is_dispatcher: bool, dispatcher_stations: list[int]) -> UserModel:
    user = UserModel(
        username=f"user_{is_dispatcher}_{'_'.join(map(str, dispatcher_stations or [0]))}",
        password_hash=hash_password("secret123"),
        is_active=True,
        gender="male",
        rating=4.8,
        can_receive_rides_for_non_payment=True,
        is_dispatcher=is_dispatcher,
        dispatcher_stations_id=dispatcher_stations,
        driver_stations_id=[],
    )
    db_session.add(user)
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


def test_dispatcher_create_ride_uses_unified_creation_flow(client, db_session):
    user = _create_user(db_session, is_dispatcher=True, dispatcher_stations=[3])
    token = _access_token_for_user(user.id)
    payload = {
        "customerPhone": "0521234567",
        "stationId": 3,
        "originText": "Main st 12",
        "destinationText": "2nd st 5",
        "notesText": "fragile package",
        "originCity": "Tel Aviv",
        "originStreet": "Main",
        "originHouseNumber": "12",
        "destinationCity": "Tel Aviv",
        "destinationStreet": "Second",
        "destinationHouseNumber": "5",
        "priceAmount": 65.5,
    }

    response = client.post("/rides", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == RideStatus.SEARCHING_DRIVER.value

    customer = db_session.query(CustomerModel).filter_by(phone_number="0521234567").one()
    ride = db_session.query(RideModel).filter_by(id=body["id"]).one()
    assert ride.customer_id == customer.id
    assert ride.dispatcher_id == user.id
    assert ride.station_id == 3

    event = db_session.query(RideEventModel).filter_by(ride_id=ride.id, event_type="RIDE_CREATED").one()
    event_payload = json.loads(event.payload_json) if isinstance(event.payload_json, str) else event.payload_json
    assert event_payload["source"] == "dispatcher"


def test_dispatcher_cannot_create_for_unassigned_station(client, db_session):
    user = _create_user(db_session, is_dispatcher=True, dispatcher_stations=[2])
    token = _access_token_for_user(user.id)
    payload = {
        "customerPhone": "0521234567",
        "stationId": 4,
        "originCity": "Tel Aviv",
        "originStreet": "Main",
        "originHouseNumber": "12",
        "destinationCity": "Tel Aviv",
        "destinationStreet": "Second",
        "destinationHouseNumber": "5",
    }

    response = client.post("/rides", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Dispatcher cannot create ride for this station"
