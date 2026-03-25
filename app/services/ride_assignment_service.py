from app.domain.enums.ride_status import RideStatus
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository


class RideAssignmentService:
    def __init__(self, ride_repository: RideRepository, ride_event_repository: RideEventRepository) -> None:
        self.ride_repository = ride_repository
        self.ride_event_repository = ride_event_repository

    def assign_driver_to_ride(self, ride_id: int, driver_id: int) -> bool:
        active = self.ride_repository.get_active_rides_for_driver(driver_id)
        if active:
            return False
        ride = self.ride_repository.get_by_id(ride_id)
        if not ride:
            return False
        self.ride_repository.assign_driver(ride, driver_id)
        self.ride_event_repository.add_event(ride.id, "DRIVER_ASSIGNED", {"driverId": driver_id})
        return True

    def mark_driver_on_the_way(self, ride_id: int) -> bool:
        ride = self.ride_repository.get_by_id(ride_id)
        if not ride:
            return False
        self.ride_repository.update_status(ride, RideStatus.DRIVER_ON_THE_WAY)
        self.ride_event_repository.add_event(ride.id, "DRIVER_ON_THE_WAY")
        return True

    def mark_picked_up(self, ride_id: int) -> bool:
        ride = self.ride_repository.get_by_id(ride_id)
        if not ride:
            return False
        self.ride_repository.update_status(ride, RideStatus.PICKED_UP)
        self.ride_event_repository.add_event(ride.id, "CUSTOMER_PICKED_UP")
        return True

    def complete_ride(self, ride_id: int) -> bool:
        ride = self.ride_repository.get_by_id(ride_id)
        if not ride:
            return False
        self.ride_repository.update_status(ride, RideStatus.COMPLETED)
        self.ride_event_repository.add_event(ride.id, "RIDE_COMPLETED")
        return True
