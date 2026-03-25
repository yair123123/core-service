from app.db.models.customer_model import CustomerModel
from app.db.models.ride_model import RideModel
from app.domain.enums.ride_status import RideStatus


def test_cancel_searching_ride(client, db_session):
    customer = CustomerModel(phone_number="0521234567")
    db_session.add(customer)
    db_session.flush()
    ride = RideModel(customer_id=customer.id, status=RideStatus.SEARCHING_DRIVER)
    db_session.add(ride)
    db_session.commit()

    response = client.post("/internal/rides/by-customer/0521234567/cancel-searching")
    assert response.status_code == 200
    assert response.json()["success"] is True

    db_session.refresh(ride)
    assert ride.status == RideStatus.CANCELED
