from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.db.models.customer_model import CustomerModel
from app.db.models.dispatcher_profile_model import DispatcherProfileModel
from app.db.models.driver_profile_model import DriverProfileModel
from app.db.models.ride_event_model import RideEventModel
from app.db.models.ride_model import RideModel
from app.db.models.station_model import StationModel
from app.db.models.station_owner_profile_model import StationOwnerProfileModel
from app.db.models.user_model import UserModel
from app.db.models.user_station_model import (
    DispatcherProfileStationModel,
    DriverProfileStationModel,
    StationOwnerProfileStationModel,
)
from app.db.session import SessionLocal
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


def _get_or_create_user(session, *, username: str, phone_number: str | None, password: str, is_active: bool = True) -> UserModel:
    user = session.execute(select(UserModel).where(UserModel.username == username)).scalar_one_or_none()
    if user is None:
        user = UserModel(
            username=username,
            phone_number=phone_number,
            password_hash=hash_password(password),
            is_active=is_active,
        )
        session.add(user)
        session.flush()
        return user

    user.phone_number = phone_number
    user.password_hash = hash_password(password)
    user.is_active = is_active
    session.flush()
    return user


def _get_or_create_driver_profile(
    session,
    *,
    user: UserModel,
    display_name: str,
    gender: str | None,
    rating: float | None,
    can_receive_rides_for_non_payment: bool,
) -> DriverProfileModel:
    profile = session.execute(select(DriverProfileModel).where(DriverProfileModel.user_id == user.id)).scalar_one_or_none()
    if profile is None:
        profile = DriverProfileModel(
            user_id=user.id,
            display_name=display_name,
            gender=gender,
            rating=rating,
            can_receive_rides_for_non_payment=can_receive_rides_for_non_payment,
        )
        session.add(profile)
        session.flush()
        return profile

    profile.display_name = display_name
    profile.gender = gender
    profile.rating = rating
    profile.can_receive_rides_for_non_payment = can_receive_rides_for_non_payment
    session.flush()
    return profile


def _get_or_create_dispatcher_profile(session, *, user: UserModel, display_name: str) -> DispatcherProfileModel:
    profile = session.execute(select(DispatcherProfileModel).where(DispatcherProfileModel.user_id == user.id)).scalar_one_or_none()
    if profile is None:
        profile = DispatcherProfileModel(user_id=user.id, display_name=display_name)
        session.add(profile)
        session.flush()
        return profile

    profile.display_name = display_name
    session.flush()
    return profile


def _get_or_create_station_owner_profile(session, *, user: UserModel, display_name: str) -> StationOwnerProfileModel:
    profile = session.execute(select(StationOwnerProfileModel).where(StationOwnerProfileModel.user_id == user.id)).scalar_one_or_none()
    if profile is None:
        profile = StationOwnerProfileModel(user_id=user.id, display_name=display_name)
        session.add(profile)
        session.flush()
        return profile

    profile.display_name = display_name
    session.flush()
    return profile


def _ensure_dispatcher_station_link(session, dispatcher_profile_id: int, station_id: int) -> None:
    existing = session.get(
        DispatcherProfileStationModel,
        {"dispatcher_profile_id": dispatcher_profile_id, "station_id": station_id},
    )
    if existing is None:
        session.add(DispatcherProfileStationModel(dispatcher_profile_id=dispatcher_profile_id, station_id=station_id))
        session.flush()


def _ensure_driver_station_link(session, driver_profile_id: int, station_id: int) -> None:
    existing = session.get(
        DriverProfileStationModel,
        {"driver_profile_id": driver_profile_id, "station_id": station_id},
    )
    if existing is None:
        session.add(DriverProfileStationModel(driver_profile_id=driver_profile_id, station_id=station_id))
        session.flush()


def _ensure_station_owner_station_link(session, station_owner_profile_id: int, station_id: int) -> None:
    existing = session.get(
        StationOwnerProfileStationModel,
        {"station_owner_profile_id": station_owner_profile_id, "station_id": station_id},
    )
    if existing is None:
        session.add(
            StationOwnerProfileStationModel(station_owner_profile_id=station_owner_profile_id, station_id=station_id)
        )
        session.flush()


def _get_or_create_ride(
    session,
    *,
    customer_id: int,
    driver_id: int | None,
    dispatcher_id: int | None,
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
        )
    ).scalar_one_or_none()
    if ride is None:
        ride = RideModel(
            customer_id=customer_id,
            driver_id=driver_id,
            dispatcher_id=dispatcher_id,
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
    ride.dispatcher_id = dispatcher_id
    ride.station_id = station_id
    ride.notes_text = notes_text
    ride.origin_city = origin_city
    ride.origin_street = origin_street
    ride.origin_house_number = origin_house_number
    ride.destination_city = destination_city
    ride.destination_street = destination_street
    ride.destination_house_number = destination_house_number
    ride.price_amount = price_amount
    ride.status = status
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


def assigned_at_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def seed() -> None:
    now = datetime.now(UTC)

    with SessionLocal() as session:
        station_tel_aviv = _get_or_create_station(session, "Tel Aviv")
        station_haifa = _get_or_create_station(session, "Haifa")
        station_jerusalem = _get_or_create_station(session, "Jerusalem")

        customer_1 = _get_or_create_customer(session, "0500000001")
        customer_2 = _get_or_create_customer(session, "0500000002")
        customer_3 = _get_or_create_customer(session, "0500000003")

        dispatcher_user = _get_or_create_user(
            session,
            username="dispatcher_demo",
            phone_number="0521000001",
            password="secret123",
        )
        dispatcher_profile = _get_or_create_dispatcher_profile(
            session,
            user=dispatcher_user,
            display_name="Dana Dispatch",
        )

        driver_user = _get_or_create_user(
            session,
            username="driver_demo",
            phone_number="0521000002",
            password="secret123",
        )
        driver_profile = _get_or_create_driver_profile(
            session,
            user=driver_user,
            display_name="David Cohen",
            gender="male",
            rating=4.7,
            can_receive_rides_for_non_payment=False,
        )

        hybrid_user = _get_or_create_user(
            session,
            username="hybrid_demo",
            phone_number="0521000003",
            password="secret123",
        )
        hybrid_driver_profile = _get_or_create_driver_profile(
            session,
            user=hybrid_user,
            display_name="Yossi Mizrahi",
            gender="male",
            rating=4.5,
            can_receive_rides_for_non_payment=True,
        )
        hybrid_dispatcher_profile = _get_or_create_dispatcher_profile(
            session,
            user=hybrid_user,
            display_name="Yossi Dispatch",
        )

        owner_user = _get_or_create_user(
            session,
            username="owner_demo",
            phone_number="0521000004",
            password="secret123",
        )
        owner_profile = _get_or_create_station_owner_profile(
            session,
            user=owner_user,
            display_name="Rachel Owner",
        )

        _ensure_dispatcher_station_link(session, dispatcher_profile.id, station_tel_aviv.id)
        _ensure_dispatcher_station_link(session, dispatcher_profile.id, station_haifa.id)
        _ensure_dispatcher_station_link(session, hybrid_dispatcher_profile.id, station_jerusalem.id)

        _ensure_driver_station_link(session, driver_profile.id, station_tel_aviv.id)
        _ensure_driver_station_link(session, driver_profile.id, station_jerusalem.id)
        _ensure_driver_station_link(session, hybrid_driver_profile.id, station_haifa.id)

        _ensure_station_owner_station_link(session, owner_profile.id, station_tel_aviv.id)
        _ensure_station_owner_station_link(session, owner_profile.id, station_haifa.id)

        ride_searching = _get_or_create_ride(
            session,
            customer_id=customer_1.id,
            driver_id=None,
            dispatcher_id=dispatcher_user.id,
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
            driver_id=driver_profile.id,
            dispatcher_id=dispatcher_user.id,
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
            driver_id=hybrid_driver_profile.id,
            dispatcher_id=hybrid_user.id,
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
            driver_id=hybrid_driver_profile.id,
            dispatcher_id=hybrid_user.id,
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
            "RIDE_CREATED",
            {
                "status": RideStatus.SEARCHING_DRIVER.value,
                "customerPhone": customer_1.phone_number,
                "stationId": station_tel_aviv.id,
                "createdByUserId": dispatcher_user.id,
            },
        )
        _ensure_ride_event(
            session,
            ride_assigned.id,
            "DRIVER_ASSIGNED",
            {
                "status": RideStatus.DRIVER_ASSIGNED.value,
                "driverProfileId": driver_profile.id,
                "driverPhone": driver_user.phone_number,
                "assignedAt": assigned_at_iso(ride_assigned.assigned_at),
            },
        )
        _ensure_ride_event(
            session,
            ride_completed.id,
            "RIDE_COMPLETED",
            {
                "status": RideStatus.COMPLETED.value,
                "driverProfileId": hybrid_driver_profile.id,
                "driverPhone": hybrid_user.phone_number,
                "completedAt": assigned_at_iso(ride_completed.completed_at),
            },
        )
        _ensure_ride_event(
            session,
            ride_canceled.id,
            "RIDE_CANCELED",
            {
                "status": RideStatus.CANCELED.value,
                "driverProfileId": hybrid_driver_profile.id,
                "driverPhone": hybrid_user.phone_number,
                "canceledAt": assigned_at_iso(ride_canceled.canceled_at),
            },
        )

        session.commit()

        print("Seed completed successfully.")
        print("Users: dispatcher_demo / driver_demo / hybrid_demo / owner_demo")
        print("Password for all users: secret123")
        print("Stations, customers, role profiles, station links, rides, and ride events were seeded.")


if __name__ == "__main__":
    seed()
