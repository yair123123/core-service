from app.db.models.customer_model import CustomerModel
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


def test_second_order_does_not_duplicate_open_ride(client, db_session):
    first = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    second = client.post("/internal/orders/process-call-order", json=PAYLOAD)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["canConfirm"] is False

    rides = db_session.query(RideModel).all()
    assert len(rides) == 1
