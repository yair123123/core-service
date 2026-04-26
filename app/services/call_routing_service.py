from app.domain.enums.ride_status import RideStatus
from app.domain.enums.routing_action import RoutingAction
from app.domain.schemas.call_routing import CallRoutingResolveResponse
from app.repositories.customer_repository import CustomerRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.ride_repository import RideRepository


class CallRoutingService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        driver_repository: DriverRepository,
        ride_repository: RideRepository,
    ) -> None:
        self.customer_repository = customer_repository
        self.driver_repository = driver_repository
        self.ride_repository = ride_repository

    def resolve(self, normalized_phone: str) -> CallRoutingResolveResponse:
        driver = self.driver_repository.get_by_phone(normalized_phone)
        if driver:
            active_rides = self.ride_repository.get_active_rides_for_driver(driver.id)
            if len(active_rides) > 1:
                return CallRoutingResolveResponse(
                    action=RoutingAction.PLAY_GENERIC_MESSAGE,
                    message="Driver has inconsistent active rides state.",
                )
            if len(active_rides) == 1:
                ride = active_rides[0]
                return CallRoutingResolveResponse(
                    action=RoutingAction.CONNECT_TO_CUSTOMER,
                    rideId=ride.id,
                    targetPhone=ride.customer.phone_number,
                )
            return CallRoutingResolveResponse(action=RoutingAction.PLAY_NO_ACTIVE_RIDE)

        customer = self.customer_repository.get_by_phone(normalized_phone)
        if not customer:
            return CallRoutingResolveResponse(action=RoutingAction.NEW_ORDER)

        open_rides = self.ride_repository.get_open_rides_for_customer(customer.id)
        if len(open_rides) > 1:
            return CallRoutingResolveResponse(
                action=RoutingAction.PLAY_GENERIC_MESSAGE,
                message="Customer has multiple open rides. Manual intervention required.",
            )
        if not open_rides:
            return CallRoutingResolveResponse(action=RoutingAction.NEW_ORDER)

        ride = open_rides[0]
        if ride.status == RideStatus.SEARCHING_DRIVER:
            return CallRoutingResolveResponse(action=RoutingAction.PLAY_SEARCHING_MESSAGE)
        if ride.status in {RideStatus.DRIVER_ASSIGNED, RideStatus.DRIVER_ON_THE_WAY} and ride.driver_profile:
            driver_phone = ride.driver_profile.user.phone_number if ride.driver_profile and ride.driver_profile.user else None
            if not driver_phone:
                return CallRoutingResolveResponse(
                    action=RoutingAction.PLAY_GENERIC_MESSAGE,
                    message="Assigned driver is missing a phone number.",
                )
            return CallRoutingResolveResponse(
                action=RoutingAction.CONNECT_TO_DRIVER,
                rideId=ride.id,
                targetPhone=driver_phone,
            )

        return CallRoutingResolveResponse(action=RoutingAction.PLAY_GENERIC_MESSAGE, message="Unhandled ride state.")
