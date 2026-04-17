import httpx

from app.config import get_settings
from app.db.models.customer_model import CustomerModel
from app.db.models.ride_model import RideModel
from app.domain.enums.ride_status import RideStatus


def _create_searching_ride(db_session, dispatch_round_number: int = 1) -> RideModel:
    customer = CustomerModel(phone_number="0528881111")
    db_session.add(customer)
    db_session.flush()
    ride = RideModel(
        customer_id=customer.id,
        station_id=7,
        status=RideStatus.SEARCHING_DRIVER,
        dispatch_round_number=dispatch_round_number,
        dispatch_current_round_id=f"ride_1_round_{dispatch_round_number}",
    )
    db_session.add(ride)
    db_session.commit()
    db_session.refresh(ride)
    return ride


def test_winner_selected_assigns_driver(client, db_session):
    ride = _create_searching_ride(db_session, dispatch_round_number=1)
    payload = {
        "rideId": ride.id,
        "roundId": f"ride_{ride.id}_round_1",
        "roundNumber": 1,
        "status": "winner_selected",
        "winnerDriverId": 55,
    }
    secret = get_settings().internal_service_secret

    response = client.post("/internal/dispatch/round-result", json=payload, headers={"X-Internal-Secret": secret})

    assert response.status_code == 200
    assert response.json()["action"] == "driver_assigned"
    db_session.refresh(ride)
    assert ride.driver_id == 55
    assert ride.status == RideStatus.DRIVER_ASSIGNED


def test_no_accept_opens_next_round(client, db_session, monkeypatch):
    ride = _create_searching_ride(db_session, dispatch_round_number=1)
    payload = {
        "rideId": ride.id,
        "roundId": f"ride_{ride.id}_round_1",
        "roundNumber": 1,
        "status": "no_accept",
    }
    calls: list[dict] = []

    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

    def _fake_post(url: str, json: dict, headers: dict, timeout: float):
        calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return _FakeResponse()

    monkeypatch.setattr(httpx, "post", _fake_post)
    secret = get_settings().internal_service_secret

    response = client.post("/internal/dispatch/round-result", json=payload, headers={"X-Internal-Secret": secret})

    assert response.status_code == 200
    assert response.json()["action"] == "next_round_started"
    db_session.refresh(ride)
    assert ride.dispatch_round_number == 2
    assert len(calls) == 1
    assert calls[0]["json"]["roundNumber"] == 2


def test_no_candidates_fails_when_policy_exhausted(client, db_session):
    ride = _create_searching_ride(db_session, dispatch_round_number=3)
    payload = {
        "rideId": ride.id,
        "roundId": f"ride_{ride.id}_round_3",
        "roundNumber": 3,
        "status": "no_candidates",
    }
    secret = get_settings().internal_service_secret

    response = client.post("/internal/dispatch/round-result", json=payload, headers={"X-Internal-Secret": secret})

    assert response.status_code == 200
    assert response.json()["action"] == "dispatch_failed"
    db_session.refresh(ride)
    assert ride.status == RideStatus.FAILED


def test_duplicate_result_is_idempotent(client, db_session):
    ride = _create_searching_ride(db_session, dispatch_round_number=1)
    payload = {
        "rideId": ride.id,
        "roundId": f"ride_{ride.id}_round_1",
        "roundNumber": 1,
        "status": "winner_selected",
        "winnerDriverId": 88,
    }
    secret = get_settings().internal_service_secret

    first = client.post("/internal/dispatch/round-result", json=payload, headers={"X-Internal-Secret": secret})
    second = client.post("/internal/dispatch/round-result", json=payload, headers={"X-Internal-Secret": secret})

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["action"] == "duplicate_ignored"
    db_session.refresh(ride)
    assert ride.driver_id == 88


def test_invalid_internal_secret_rejected(client, db_session):
    ride = _create_searching_ride(db_session, dispatch_round_number=1)
    payload = {
        "rideId": ride.id,
        "roundId": f"ride_{ride.id}_round_1",
        "roundNumber": 1,
        "status": "round_expired",
    }

    response = client.post("/internal/dispatch/round-result", json=payload, headers={"X-Internal-Secret": "bad-secret"})

    assert response.status_code == 403
