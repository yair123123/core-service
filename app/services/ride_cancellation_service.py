from app.domain.enums.ride_status import RideStatus
from app.domain.schemas.ride_confirmation import CancelSearchingRideResponse
from app.repositories.customer_repository import CustomerRepository
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository
from app.services.phone_normalizer import PhoneNormalizer


class RideCancellationService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        ride_repository: RideRepository,
        ride_event_repository: RideEventRepository,
        phone_normalizer: PhoneNormalizer,
    ) -> None:
        self.customer_repository = customer_repository
        self.ride_repository = ride_repository
        self.ride_event_repository = ride_event_repository
        self.phone_normalizer = phone_normalizer

    def cancel_searching_ride(self, phone: str) -> CancelSearchingRideResponse:
        normalized = self.phone_normalizer.normalize_israeli_phone(phone)
        customer = self.customer_repository.get_by_phone(normalized)
        if not customer:
            return CancelSearchingRideResponse(success=False)

        open_rides = self.ride_repository.get_open_rides_for_customer(customer.id)
        searching = [ride for ride in open_rides if ride.status == RideStatus.SEARCHING_DRIVER]
        if len(searching) != 1:
            return CancelSearchingRideResponse(success=False)

        ride = searching[0]
        self.ride_repository.cancel_ride(ride)
        self.ride_event_repository.add_event(ride.id, "RIDE_CANCELED_BY_CUSTOMER")
        return CancelSearchingRideResponse(success=True)
