from app.domain.enums.ride_status import RideStatus
from app.domain.schemas.ride_order_processing import ProcessCallOrderRequest, ProcessCallOrderResponse
from app.repositories.customer_repository import CustomerRepository
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository
from app.services.phone_normalizer import PhoneNormalizer
from app.services.pricing_service import PricingService
from app.services.speech_processing_adapter import SpeechProcessingAdapter


class RideOrderService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        ride_repository: RideRepository,
        ride_event_repository: RideEventRepository,
        phone_normalizer: PhoneNormalizer,
        speech_processing_adapter: SpeechProcessingAdapter,
        pricing_service: PricingService,
    ) -> None:
        self.customer_repository = customer_repository
        self.ride_repository = ride_repository
        self.ride_event_repository = ride_event_repository
        self.phone_normalizer = phone_normalizer
        self.speech_processing_adapter = speech_processing_adapter
        self.pricing_service = pricing_service

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

        ride = self.ride_repository.create_ride(
            customer_id=customer.id,
            status=RideStatus.SEARCHING_DRIVER,
            origin_text=speech.origin_text,
            destination_text=speech.destination_text,
            notes_text=speech.notes_text,
            origin_city=speech.origin_city,
            origin_street=speech.origin_street,
            origin_house_number=speech.origin_house_number,
            destination_city=speech.destination_city,
            destination_street=speech.destination_street,
            destination_house_number=speech.destination_house_number,
            price_amount=price,
        )
        self.ride_event_repository.add_event(ride.id, "RIDE_CREATED", {"callSessionId": payload.call_session_id})

        summary = f"Ride from {speech.origin_street} {speech.origin_house_number} to {speech.destination_street} {speech.destination_house_number}."
        return ProcessCallOrderResponse(success=True, rideId=ride.id, summaryText=summary, canConfirm=True)
