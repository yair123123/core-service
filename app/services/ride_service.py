from app.domain.schemas.auth import CurrentUserResponse
from app.domain.schemas.ride import RideRead
from app.repositories.ride_repository import RideRepository


class RideService:
    def __init__(self, ride_repository: RideRepository) -> None:
        self.ride_repository = ride_repository

    def get_my_driver_rides(self, current_user: CurrentUserResponse) -> list[RideRead]:
        if current_user.driver_profile_id is None:
            return []

        station_ids = current_user.driver_stations_id
        if not station_ids:
            return []

        rides = self.ride_repository.get_open_rides_for_station_ids(station_ids)
        return [RideRead.model_validate(ride) for ride in rides]
