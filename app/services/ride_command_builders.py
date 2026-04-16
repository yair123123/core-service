from dataclasses import dataclass
from decimal import Decimal

from app.domain.schemas.auth import CurrentUserResponse
from app.domain.schemas.ride_order_processing import ProcessCallOrderRequest
from app.domain.schemas.ride_request import CreateRideFromDispatcherRequest
from app.services.speech_processing_adapter import ProcessedOrderSpeech
from app.services.ride_creation_service import CreateRideCommand


@dataclass(slots=True)
class CreateRideFromPhoneInput:
    payload: ProcessCallOrderRequest
    customer_id: int
    speech: ProcessedOrderSpeech
    price: Decimal | float | None


class DispatcherRideCommandBuilder:
    def build(self, payload: CreateRideFromDispatcherRequest, current_user: CurrentUserResponse, customer_id: int) -> CreateRideCommand:
        return CreateRideCommand(
            customer_id=customer_id,
            origin_text=payload.origin_text,
            destination_text=payload.destination_text,
            notes_text=payload.notes_text,
            origin_city=payload.origin_city,
            origin_street=payload.origin_street,
            origin_house_number=payload.origin_house_number,
            destination_city=payload.destination_city,
            destination_street=payload.destination_street,
            destination_house_number=payload.destination_house_number,
            price_amount=payload.price_amount,
            station_id=payload.station_id,
            dispatcher_id=current_user.id,
            metadata={"source": "dispatcher", "createdByUserId": current_user.id},
        )


class PhoneRideCommandBuilder:
    def build(self, payload: CreateRideFromPhoneInput) -> CreateRideCommand:
        speech = payload.speech
        return CreateRideCommand(
            customer_id=payload.customer_id,
            origin_text=speech.origin_text,
            destination_text=speech.destination_text,
            notes_text=speech.notes_text,
            origin_city=speech.origin_city,
            origin_street=speech.origin_street,
            origin_house_number=speech.origin_house_number,
            destination_city=speech.destination_city,
            destination_street=speech.destination_street,
            destination_house_number=speech.destination_house_number,
            price_amount=payload.price,
            metadata={"source": "phone", "callSessionId": payload.payload.call_session_id},
        )
