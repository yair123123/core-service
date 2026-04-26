from fastapi import HTTPException, status

from app.domain.schemas.auth import CurrentUserResponse
from app.domain.schemas.ride_request import CreateRideFromDispatcherRequest
from app.repositories.customer_repository import CustomerRepository
from app.services.address_service import AddressInput, AddressResolutionError, AddressService
from app.services.phone_normalizer import PhoneNormalizer
from app.services.ride_command_builders import CreateRideFromDispatcherInput, DispatcherRideCommandBuilder
from app.services.ride_creation_service import RideCreationService


class DispatcherRideService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        phone_normalizer: PhoneNormalizer,
        dispatcher_command_builder: DispatcherRideCommandBuilder,
        address_service: AddressService,
        ride_creation_service: RideCreationService,
    ) -> None:
        self.customer_repository = customer_repository
        self.phone_normalizer = phone_normalizer
        self.dispatcher_command_builder = dispatcher_command_builder
        self.address_service = address_service
        self.ride_creation_service = ride_creation_service

    def create_ride(self, payload: CreateRideFromDispatcherRequest, current_user: CurrentUserResponse):
        if current_user.dispatcher_profile_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dispatcher role is required")
        if payload.station_id not in current_user.dispatcher_stations_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dispatcher cannot create ride for this station")

        phone = self.phone_normalizer.normalize_israeli_phone(payload.customer_phone)
        customer = self.customer_repository.get_or_create_by_phone(phone)

        try:
            origin_address, destination_address = self.address_service.resolve_and_create_address_batch(
                AddressInput(
                    city=payload.origin_city,
                    street=payload.origin_street,
                    house_number=payload.origin_house_number,
                ),
                AddressInput(
                    city=payload.destination_city,
                    street=payload.destination_street,
                    house_number=payload.destination_house_number,
                ),
            )
        except AddressResolutionError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        command = self.dispatcher_command_builder.build(
            CreateRideFromDispatcherInput(
                payload=payload,
                current_user=current_user,
                customer_id=customer.id,
                origin_address_id=origin_address.id,
                destination_address_id=destination_address.id,
            )
        )
        return self.ride_creation_service.create_ride(command)
