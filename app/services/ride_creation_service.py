from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.domain.enums.ride_status import RideStatus
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository


@dataclass(slots=True)
class CreateRideCommand:
    customer_id: int
    origin_text: str | None
    destination_text: str | None
    notes_text: str | None
    origin_city: str | None
    origin_street: str | None
    origin_house_number: str | None
    destination_city: str | None
    destination_street: str | None
    destination_house_number: str | None
    price_amount: Decimal | float | None
    station_id: int | None = None
    dispatcher_id: int | None = None
    metadata: dict[str, Any] | None = None


class RideCreationService:
    def __init__(self, ride_repository: RideRepository, ride_event_repository: RideEventRepository) -> None:
        self.ride_repository = ride_repository
        self.ride_event_repository = ride_event_repository

    def create_ride(self, command: CreateRideCommand):
        ride = self.ride_repository.create_ride(
            customer_id=command.customer_id,
            status=RideStatus.SEARCHING_DRIVER,
            origin_text=command.origin_text,
            destination_text=command.destination_text,
            notes_text=command.notes_text,
            origin_city=command.origin_city,
            origin_street=command.origin_street,
            origin_house_number=command.origin_house_number,
            destination_city=command.destination_city,
            destination_street=command.destination_street,
            destination_house_number=command.destination_house_number,
            price_amount=command.price_amount,
            station_id=command.station_id,
            dispatcher_id=command.dispatcher_id,
        )
        self.ride_event_repository.add_event(ride.id, "RIDE_CREATED", command.metadata or {})
        return ride
