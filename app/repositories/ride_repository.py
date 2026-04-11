from datetime import datetime, UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.ride_model import RideModel
from app.domain.enums.ride_status import RideStatus


OPEN_RIDE_STATUSES = {
    RideStatus.SEARCHING_DRIVER,
    RideStatus.DRIVER_ASSIGNED,
    RideStatus.DRIVER_ON_THE_WAY,
    RideStatus.PICKED_UP,
}

DRIVER_ACTIVE_STATUSES = {RideStatus.DRIVER_ASSIGNED, RideStatus.DRIVER_ON_THE_WAY}


class RideRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, ride_id: int) -> RideModel | None:
        return self.db.get(RideModel, ride_id)

    def get_open_rides_for_customer(self, customer_id: int) -> list[RideModel]:
        stmt = select(RideModel).where(RideModel.customer_id == customer_id, RideModel.status.in_(OPEN_RIDE_STATUSES))
        return list(self.db.scalars(stmt).all())

    def get_active_rides_for_driver(self, driver_id: int) -> list[RideModel]:
        stmt = select(RideModel).where(RideModel.driver_id == driver_id, RideModel.status.in_(DRIVER_ACTIVE_STATUSES))
        return list(self.db.scalars(stmt).all())

    def get_open_rides_for_station_ids(self, station_ids: list[int]) -> list[RideModel]:
        if not station_ids:
            return []
        stmt = select(RideModel).where(RideModel.station_id.in_(station_ids), RideModel.status.in_(OPEN_RIDE_STATUSES))
        return list(self.db.scalars(stmt).all())

    def create_ride(self, customer_id: int, status: RideStatus, **fields: Any) -> RideModel:
        ride = RideModel(customer_id=customer_id, status=status, **fields)
        self.db.add(ride)
        self.db.flush()
        return ride

    def assign_driver(self, ride: RideModel, driver_id: int) -> RideModel:
        ride.driver_id = driver_id
        ride.status = RideStatus.DRIVER_ASSIGNED
        ride.assigned_at = datetime.now(UTC)
        self.db.flush()
        return ride

    def update_status(self, ride: RideModel, status: RideStatus) -> RideModel:
        ride.status = status
        if status == RideStatus.DRIVER_ON_THE_WAY:
            ride.assigned_at = ride.assigned_at or datetime.now(UTC)
        elif status == RideStatus.COMPLETED:
            ride.completed_at = datetime.now(UTC)
        elif status == RideStatus.CANCELED:
            ride.canceled_at = datetime.now(UTC)
        self.db.flush()
        return ride

    def confirm_ride(self, ride: RideModel) -> RideModel:
        ride.confirmed_at = datetime.now(UTC)
        self.db.flush()
        return ride

    def cancel_ride(self, ride: RideModel) -> RideModel:
        ride.status = RideStatus.CANCELED
        ride.canceled_at = datetime.now(UTC)
        self.db.flush()
        return ride
