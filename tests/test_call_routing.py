from app.db.models.customer_model import CustomerModel
from app.db.models.driver_profile_model import DriverProfileModel
from app.db.models.ride_model import RideModel
from app.domain.enums.ride_status import RideStatus


def test_customer_no_ride_new_order(client):
    response = client.post("/internal/call-routing/resolve", json={"phone": "0521234567"})
    assert response.status_code == 200
    assert response.json()["action"] == "NEW_ORDER"


def test_customer_searching_message(client, db_session):
    customer = CustomerModel(phone_number="0521234567")
    db_session.add(customer)
    db_session.flush()
    db_session.add(RideModel(customer_id=customer.id, status=RideStatus.SEARCHING_DRIVER))
    db_session.commit()

    response = client.post("/internal/call-routing/resolve", json={"phone": "0521234567"})
    assert response.json()["action"] == "PLAY_SEARCHING_MESSAGE"


def test_customer_assigned_connect_to_driver(client, db_session):
    customer = CustomerModel(phone_number="0521234567")
    driver = DriverProfileModel(phone_number="0501112233", is_active=True)
    db_session.add_all([customer, driver])
    db_session.flush()
    db_session.add(RideModel(customer_id=customer.id, driver_id=driver.id, status=RideStatus.DRIVER_ASSIGNED))
    db_session.commit()

    response = client.post("/internal/call-routing/resolve", json={"phone": "0521234567"})
    body = response.json()
    assert body["action"] == "CONNECT_TO_DRIVER"
    assert body["targetPhone"] == "0501112233"


def test_driver_active_connect_to_customer(client, db_session):
    customer = CustomerModel(phone_number="0521234567")
    driver = DriverProfileModel(phone_number="0501112233", is_active=True)
    db_session.add_all([customer, driver])
    db_session.flush()
    db_session.add(RideModel(customer_id=customer.id, driver_id=driver.id, status=RideStatus.DRIVER_ON_THE_WAY))
    db_session.commit()

    response = client.post("/internal/call-routing/resolve", json={"phone": "0501112233"})
    body = response.json()
    assert body["action"] == "CONNECT_TO_CUSTOMER"
    assert body["targetPhone"] == "0521234567"


def test_driver_without_active_ride(client, db_session):
    db_session.add(DriverProfileModel(phone_number="0501112233", is_active=True))
    db_session.commit()

    response = client.post("/internal/call-routing/resolve", json={"phone": "0501112233"})
    assert response.json()["action"] == "PLAY_NO_ACTIVE_RIDE"
