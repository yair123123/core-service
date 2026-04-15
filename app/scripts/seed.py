from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.db.session import SessionLocal
from app.db.models.customer_model import CustomerModel
from app.db.models.driver_profile_model import DriverProfileModel
from app.db.models.ride_event_model import RideEventModel
from app.db.models.ride_model import RideModel
from app.db.models.station_model import StationModel
from app.db.models.user_model import UserModel
from app.db.models.user_station_model import UserDispatcherStationModel, UserDriverStationModel
from app.domain.enums.ride_status import RideStatus
from app.services.security import hash_password


def _get_or_create_station(session, name: str, is_active: bool = True) -> StationModel:
    station = session.execute(select(StationModel).where(StationModel.name == name)).scalar_one_or_none()
    if station is None:
        station = StationModel(name=name, is_active=is_active)
        session.add(station)
        session.flush()
        return station

    station.is_active = is_active
    session.flush()
    return station


def _get_or_create_customer(session, phone_number: str) -> CustomerModel:
    customer = session.execute(select(CustomerModel).where(CustomerModel.phone_number == phone_number)).scalar_one_or_none()
    if customer is None:
        customer = CustomerModel(phone_number=phone_number)
        session.add(customer)
        session.flush()
    return customer


def _get_or_create_driver(session, phone_number: str, name: str, is_active: bool = True) -> DriverProfileModel:
    driver = session.execute(select(DriverProfileModel).where(DriverProfileModel.phone_number == phone_number)).scalar_one_or_none()
    if driver is None:
        driver = DriverProfileModel(phone_number=phone_number, name=name, is_active=is_active)
        session.add(driver)
        session.flush()
        return driver

    driver.name = name
    driver.is_active = is_active
    session.flush()
    return driver


def _get_or_create_user(
    session,
    *,
    username: str,
    password: str,
    gender: str,
    rating: float,
    can_receive_rides_for_non_payment: bool,
    is_dispatcher: bool,
    dispatcher_stations_id: list[int],
    driver_stations_id: list[int],
) -> UserModel:
    user = session.execute(select(UserModel).where(UserModel.username == username)).scalar_one_or_none()
    if user is None:
        user = UserModel(
            username=username,
            password_hash=hash_password(password),
            is_active=True,
            gender=gender,
            rating=rating,
            can_receive_rides_for_non_payment=can_receive_rides_for_non_payment,
            is_dispatcher=is_dispatcher,
            dispatcher_stations_id=dispatcher_stations_id,
            driver_stations_id=driver_stations_id,
        )
        session.add(user)
        session.flush()
        return user

    user.password_hash = hash_password(password)
    user.is_active = True
    user.gender = gender
    user.rating = rating
    user.can_receive_rides_for_non_payment = can_receive_rides_for_non_payment
    user.is_dispatcher = is_dispatcher
    user.dispatcher_stations_id = dispatcher_stations_id
    user.driver_stations_id = driver_stations_id
    session.flush()
    return user


def _ensure_dispatcher_station_link(session, user_id: int, station_id: int) -> None:
    existing = session.get(UserDispatcherStationModel, {"user_id": user_id, "station_id": station_id})
    if existing is None:
        session.add(UserDispatcherStationModel(user_id=user_id, station_id=station_id))
        session.flush()


def _ensure_driver_station_link(session, user_id: int, station_id: int) -> None:
    existing = session.get(UserDriverStationModel, {"user_id": user_id, "station_id": station_id})
    if existing is None:
        session.add(UserDriverStationModel(user_id=user_id, station_id=station_id))
        session.flush()


def _get_or_create_ride(
    session,
    *,
    customer_id: int,
    driver_id: int | None,
    station_id: int | None,
    origin_text: str,
    destination_text: str,
    notes_text: str | None,
    origin_city: str,
    origin_street: str,
    origin_house_number: str,
    destination_city: str,
    destination_street: str,
    destination_house_number: str,
    price_amount: Decimal | None,
    status: RideStatus,
    assigned_at: datetime | None = None,
    confirmed_at: datetime | None = None,
    canceled_at: datetime | None = None,
    completed_at: datetime | None = None,
) -> RideModel:
    ride = session.execute(
        select(RideModel).where(
            RideModel.customer_id == customer_id,
            RideModel.origin_text == origin_text,
            RideModel.destination_text == destination_text,
            RideModel.status == status,
        )
    ).scalar_one_or_none()
    if ride is None:
        ride = RideModel(
            customer_id=customer_id,
            driver_id=driver_id,
            station_id=station_id,
            origin_text=origin_text,
            destination_text=destination_text,
            notes_text=notes_text,
            origin_city=origin_city,
            origin_street=origin_street,
            origin_house_number=origin_house_number,
            destination_city=destination_city,
            destination_street=destination_street,
            destination_house_number=destination_house_number,
            price_amount=price_amount,
            status=status,
            assigned_at=assigned_at,
            confirmed_at=confirmed_at,
            canceled_at=canceled_at,
            completed_at=completed_at,
        )
        session.add(ride)
        session.flush()
        return ride

    ride.driver_id = driver_id
    ride.station_id = station_id
    ride.notes_text = notes_text
    ride.origin_city = origin_city
    ride.origin_street = origin_street
    ride.origin_house_number = origin_house_number
    ride.destination_city = destination_city
    ride.destination_street = destination_street
    ride.destination_house_number = destination_house_number
    ride.price_amount = price_amount
    ride.assigned_at = assigned_at
    ride.confirmed_at = confirmed_at
    ride.canceled_at = canceled_at
    ride.completed_at = completed_at
    session.flush()
    return ride


def _ensure_ride_event(session, ride_id: int, event_type: str, payload_json: dict | str | None) -> None:
    event = session.execute(
        select(RideEventModel).where(RideEventModel.ride_id == ride_id, RideEventModel.event_type == event_type)
    ).scalar_one_or_none()
    if event is None:
        event = RideEventModel(ride_id=ride_id, event_type=event_type, payload_json=payload_json)
        session.add(event)
    else:
        event.payload_json = payload_json
    session.flush()


def seed() -> None:
    now = datetime.now(UTC)

    with SessionLocal() as session:
        station_tel_aviv = _get_or_create_station(session, "Tel Aviv")
        station_haifa = _get_or_create_station(session, "Haifa")
        station_jerusalem = _get_or_create_station(session, "Jerusalem")

        customer_1 = _get_or_create_customer(session, "0500000001")
        customer_2 = _get_or_create_customer(session, "0500000002")
        customer_3 = _get_or_create_customer(session, "0500000003")

        driver_1 = _get_or_create_driver(session, "0520000001", "David Cohen", is_active=True)
        driver_2 = _get_or_create_driver(session, "0520000002", "Moshe Levi", is_active=True)
        driver_3 = _get_or_create_driver(session, "0520000003", "Yossi Mizrahi", is_active=False)

        dispatcher_user = _get_or_create_user(
            session,
            username="dispatcher_demo",
            password="secret123",
            gender="male",
            rating=4.9,
            can_receive_rides_for_non_payment=True,
            is_dispatcher=True,
            dispatcher_stations_id=[station_tel_aviv.id, station_haifa.id],
            driver_stations_id=[],
        )
        driver_user = _get_or_create_user(
            session,
            username="driver_demo",
            password="secret123",
            gender="female",
            rating=4.7,
            can_receive_rides_for_non_payment=False,
            is_dispatcher=False,
            dispatcher_stations_id=[],
            driver_stations_id=[station_tel_aviv.id, station_jerusalem.id],
        )
        hybrid_user = _get_or_create_user(
            session,
            username="hybrid_demo",
            password="secret123",
            gender="male",
            rating=4.5,
            can_receive_rides_for_non_payment=True,
            is_dispatcher=True,
            dispatcher_stations_id=[station_jerusalem.id],
            driver_stations_id=[station_haifa.id],
        )

        _ensure_dispatcher_station_link(session, dispatcher_user.id, station_tel_aviv.id)
        _ensure_dispatcher_station_link(session, dispatcher_user.id, station_haifa.id)
        _ensure_dispatcher_station_link(session, hybrid_user.id, station_jerusalem.id)

        _ensure_driver_station_link(session, driver_user.id, station_tel_aviv.id)
        _ensure_driver_station_link(session, driver_user.id, station_jerusalem.id)
        _ensure_driver_station_link(session, hybrid_user.id, station_haifa.id)

        ride_searching = _get_or_create_ride(
            session,
            customer_id=customer_1.id,
            driver_id=None,
            station_id=station_tel_aviv.id,
            origin_text="Dizengoff 100, Tel Aviv",
            destination_text="Ben Yehuda 50, Tel Aviv",
            notes_text="Customer with small bag",
            origin_city="Tel Aviv",
            origin_street="Dizengoff",
            origin_house_number="100",
            destination_city="Tel Aviv",
            destination_street="Ben Yehuda",
            destination_house_number="50",
            price_amount=Decimal("25.00"),
            status=RideStatus.SEARCHING_DRIVER,
        )
        ride_assigned = _get_or_create_ride(
            session,
            customer_id=customer_2.id,
            driver_id=driver_1.id,
            station_id=station_haifa.id,
            origin_text="Herzl 12, Haifa",
            destination_text="Haneviim 5, Haifa",
            notes_text="Call before arrival",
            origin_city="Haifa",
            origin_street="Herzl",
            origin_house_number="12",
            destination_city="Haifa",
            destination_street="Haneviim",
            destination_house_number="5",
            price_amount=Decimal("32.50"),
            status=RideStatus.DRIVER_ASSIGNED,
            assigned_at=now - timedelta(minutes=20),
            confirmed_at=now - timedelta(minutes=18),
        )
        ride_completed = _get_or_create_ride(
            session,
            customer_id=customer_3.id,
            driver_id=driver_2.id,
            station_id=station_jerusalem.id,
            origin_text="Jaffa 1, Jerusalem",
            destination_text="King George 22, Jerusalem",
            notes_text="Paid in cash",
            origin_city="Jerusalem",
            origin_street="Jaffa",
            origin_house_number="1",
            destination_city="Jerusalem",
            destination_street="King George",
            destination_house_number="22",
            price_amount=Decimal("41.00"),
            status=RideStatus.COMPLETED,
            assigned_at=now - timedelta(hours=2),
            confirmed_at=now - timedelta(hours=1, minutes=50),
            completed_at=now - timedelta(hours=1, minutes=10),
        )
        ride_canceled = _get_or_create_ride(
            session,
            customer_id=customer_1.id,
            driver_id=driver_3.id,
            station_id=station_tel_aviv.id,
            origin_text="Allenby 44, Tel Aviv",
            destination_text="Rothschild 10, Tel Aviv",
            notes_text="Canceled by customer",
            origin_city="Tel Aviv",
            origin_street="Allenby",
            origin_house_number="44",
            destination_city="Tel Aviv",
            destination_street="Rothschild",
            destination_house_number="10",
            price_amount=Decimal("28.00"),
            status=RideStatus.CANCELED,
            assigned_at=now - timedelta(hours=4),
            confirmed_at=now - timedelta(hours=4, minutes=5),
            canceled_at=now - timedelta(hours=3, minutes=45),
        )

        _ensure_ride_event(
            session,
            ride_searching.id,
            "ride_created",
            {
                "status": RideStatus.SEARCHING_DRIVER.value,
                "customerPhone": customer_1.phone_number,
                "stationId": station_tel_aviv.id,
            },
        )
        _ensure_ride_event(
            session,
            ride_assigned.id,
            "driver_assigned",
            {
                "status": RideStatus.DRIVER_ASSIGNED.value,
                "driverPhone": driver_1.phone_number,
                "assignedAt": assigned_at_iso(ride_assigned.assigned_at),
            },
        )
        _ensure_ride_event(
            session,
            ride_completed.id,
            "ride_completed",
            {
                "status": RideStatus.COMPLETED.value,
                "driverPhone": driver_2.phone_number,
                "completedAt": assigned_at_iso(ride_completed.completed_at),
            },
        )
        _ensure_ride_event(
            session,
            ride_canceled.id,
            "ride_canceled",
            {
                "status": RideStatus.CANCELED.value,
                "driverPhone": driver_3.phone_number,
                "canceledAt": assigned_at_iso(ride_canceled.canceled_at),
            },
        )

        session.commit()

        print("Seed completed successfully.")
        print("Users: dispatcher_demo / driver_demo / hybrid_demo")
        print("Password for all users: secret123")
        print("Stations, customers, drivers, rides, ride events and station links were seeded.")


def assigned_at_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


if __name__ == "__main__":
    seed()
