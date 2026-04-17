import json

import httpx

from app.db.models.address_model import AddressModel
from app.db.models.customer_model import CustomerModel
from app.db.models.ride_event_model import RideEventModel
from app.db.models.ride_model import RideModel
from app.domain.enums.ride_status import RideStatus

PAYLOAD = {
    "callSessionId": "abc",
    "fromPhone": "0521234567",
    "originRecordingUrl": "https://example.com/origin",
    "destinationRecordingUrl": "https://example.com/destination",
    "notesRecordingUrl": "https://example.com/notes",
}


def _mock_geocode_batch(monkeypatch):
    class _FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "success": True,
                "results": [
                    {
                        "success": True,
                        "query": {
                            "city": "Tel Aviv",
                            "street": "Herzl",
                            "house_number": "10",
                            "country_code": "IL",
                        },
                        "result": {
                            "lat": 32.1,
                            "lon": 34.8,
                            "formatted_address": "Herzl 10, Tel Aviv",
                            "provider": "mapbox",
                            "provider_place_id": "x",
                            "match_quality": "high",
                            "partial_match": False,
                        },
                        "warnings": [],
                        "error": None,
                    },
                    {
                        "success": True,
                        "query": {
                            "city": "Tel Aviv",
                            "street": "Allenby",
                            "house_number": "5",
                            "country_code": "IL",
                        },
                        "result": {
                            "lat": 32.2,
                            "lon": 34.9,
                            "formatted_address": "Allenby 5, Tel Aviv",
                            "provider": "mapbox",
                            "provider_place_id": "y",
                            "match_quality": "high",
                            "partial_match": False,
                        },
                        "warnings": [],
                        "error": None,
                    },
                ],
                "warnings": [],
                "error": None,
            }

    def _fake_post(url: str, json: dict, timeout: float):
        assert url.endswith("/v1/geocode/batch")
        return _FakeResponse()

    monkeypatch.setattr(httpx, "post", _fake_post)


def test_process_call_order_creates_ride(client, db_session, monkeypatch):
    _mock_geocode_batch(monkeypatch)
    response = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    body = response.json()
    assert body["success"] is True
    assert body["canConfirm"] is True

    customer = db_session.query(CustomerModel).filter_by(phone_number="0521234567").one()
    ride = db_session.query(RideModel).filter_by(customer_id=customer.id).one()
    assert ride.status == RideStatus.SEARCHING_DRIVER
    assert ride.origin_address_id is not None
    assert ride.destination_address_id is not None
    assert db_session.query(AddressModel).count() == 2

    event = db_session.query(RideEventModel).filter_by(ride_id=ride.id, event_type="RIDE_CREATED").one()
    event_payload = json.loads(event.payload_json) if isinstance(event.payload_json, str) else event.payload_json
    assert event_payload == {"source": "phone", "callSessionId": "abc"}


def test_second_order_does_not_duplicate_open_ride(client, db_session, monkeypatch):
    _mock_geocode_batch(monkeypatch)
    first = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    second = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["canConfirm"] is False

    rides = db_session.query(RideModel).all()
    assert len(rides) == 1
