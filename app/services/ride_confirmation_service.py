from app.domain.schemas.ride_confirmation import ConfirmRideResponse
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository


class RideConfirmationService:
    def __init__(self, ride_repository: RideRepository, ride_event_repository: RideEventRepository) -> None:
        self.ride_repository = ride_repository
        self.ride_event_repository = ride_event_repository

    def confirm_ride(self, ride_id: int) -> ConfirmRideResponse:
        ride = self.ride_repository.get_by_id(ride_id)
        if not ride:
            return ConfirmRideResponse(success=False)
        self.ride_repository.confirm_ride(ride)
        self.ride_event_repository.add_event(ride_id, "RIDE_CONFIRMED")
        return ConfirmRideResponse(success=True)
