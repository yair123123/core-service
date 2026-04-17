from fastapi import HTTPException, status

from app.domain.schemas.ride_order_processing import ProcessCallOrderRequest, ProcessCallOrderResponse
from app.repositories.customer_repository import CustomerRepository
from app.repositories.ride_repository import RideRepository
from app.services.address_service import AddressInput, AddressResolutionError, AddressService
from app.services.phone_normalizer import PhoneNormalizer
from app.services.pricing_service import PricingService
from app.services.ride_command_builders import CreateRideFromPhoneInput, PhoneRideCommandBuilder
from app.services.ride_creation_service import RideCreationService
from app.services.speech_processing_adapter import SpeechProcessingAdapter


class RideOrderService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        ride_repository: RideRepository,
        phone_normalizer: PhoneNormalizer,
        speech_processing_adapter: SpeechProcessingAdapter,
        pricing_service: PricingService,
        phone_command_builder: PhoneRideCommandBuilder,
        address_service: AddressService,
        ride_creation_service: RideCreationService,
    ) -> None:
        self.customer_repository = customer_repository
        self.ride_repository = ride_repository
        self.phone_normalizer = phone_normalizer
        self.speech_processing_adapter = speech_processing_adapter
        self.pricing_service = pricing_service
        self.phone_command_builder = phone_command_builder
        self.address_service = address_service
        self.ride_creation_service = ride_creation_service

    def process_call_order(self, payload: ProcessCallOrderRequest) -> ProcessCallOrderResponse:
        phone = self.phone_normalizer.normalize_israeli_phone(payload.from_phone)
        customer = self.customer_repository.get_or_create_by_phone(phone)

        open_rides = self.ride_repository.get_open_rides_for_customer(customer.id)
        if open_rides:
            existing = open_rides[0]
            return ProcessCallOrderResponse(
                success=True,
                rideId=existing.id,
                summaryText="You already have an open ride request.",
                canConfirm=False,
            )

        speech = self.speech_processing_adapter.process_order_recordings(
            payload.origin_recording_url,
            payload.destination_recording_url,
            payload.notes_recording_url,
        )
        price = self.pricing_service.compute_price(speech.origin_city, speech.destination_city)

        try:
            origin_address, destination_address = self.address_service.resolve_and_create_address_batch(
                AddressInput(
                    city=speech.origin_city,
                    street=speech.origin_street,
                    house_number=speech.origin_house_number,
                ),
                AddressInput(
                    city=speech.destination_city,
                    street=speech.destination_street,
                    house_number=speech.destination_house_number,
                ),
            )
        except AddressResolutionError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        command = self.phone_command_builder.build(
            CreateRideFromPhoneInput(
                payload=payload,
                customer_id=customer.id,
                speech=speech,
                price=price,
                origin_address_id=origin_address.id,
                destination_address_id=destination_address.id,
            )
        )
        ride = self.ride_creation_service.create_ride(command)

        summary = f"Ride from {speech.origin_street} {speech.origin_house_number} to {speech.destination_street} {speech.destination_house_number}."
        return ProcessCallOrderResponse(success=True, rideId=ride.id, summaryText=summary, canConfirm=True)
