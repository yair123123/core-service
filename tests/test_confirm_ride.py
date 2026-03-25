from app.db.models.customer_model import CustomerModel
from app.db.models.ride_model import RideModel
from app.domain.enums.ride_status import RideStatus


def test_confirm_ride(client, db_session):
    customer = CustomerModel(phone_number="0521234567")
    db_session.add(customer)
    db_session.flush()
    ride = RideModel(customer_id=customer.id, status=RideStatus.SEARCHING_DRIVER)
    db_session.add(ride)
    db_session.commit()

    response = client.post(f"/internal/rides/{ride.id}/confirm")
    assert response.status_code == 200
    assert response.json()["success"] is True
