import json

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


def test_process_call_order_creates_ride(client, db_session):
    response = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    body = response.json()
    assert body["success"] is True
    assert body["canConfirm"] is True

    customer = db_session.query(CustomerModel).filter_by(phone_number="0521234567").one()
    ride = db_session.query(RideModel).filter_by(customer_id=customer.id).one()
    assert ride.status == RideStatus.SEARCHING_DRIVER

    event = db_session.query(RideEventModel).filter_by(ride_id=ride.id, event_type="RIDE_CREATED").one()
    event_payload = json.loads(event.payload_json) if isinstance(event.payload_json, str) else event.payload_json
    assert event_payload == {"source": "phone", "callSessionId": "abc"}


def test_second_order_does_not_duplicate_open_ride(client, db_session):
    first = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    second = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["canConfirm"] is False

    rides = db_session.query(RideModel).all()
    assert len(rides) == 1
