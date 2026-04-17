from dataclasses import dataclass
from decimal import Decimal

from app.domain.schemas.auth import CurrentUserResponse
from app.domain.schemas.ride_order_processing import ProcessCallOrderRequest
from app.domain.schemas.ride_request import CreateRideFromDispatcherRequest
from app.services.ride_creation_service import CreateRideCommand
from app.services.speech_processing_adapter import ProcessedOrderSpeech


@dataclass(slots=True)
class CreateRideFromPhoneInput:
    payload: ProcessCallOrderRequest
    customer_id: int
    speech: ProcessedOrderSpeech
    price: Decimal | float | None
    origin_address_id: int
    destination_address_id: int


@dataclass(slots=True)
class CreateRideFromDispatcherInput:
    payload: CreateRideFromDispatcherRequest
    current_user: CurrentUserResponse
    customer_id: int
    origin_address_id: int
    destination_address_id: int


class DispatcherRideCommandBuilder:
    def build(self, payload: CreateRideFromDispatcherInput) -> CreateRideCommand:
        request = payload.payload
        return CreateRideCommand(
            customer_id=payload.customer_id,
            origin_text=request.origin_text,
            destination_text=request.destination_text,
            notes_text=request.notes_text,
            origin_city=request.origin_city,
            origin_street=request.origin_street,
            origin_house_number=request.origin_house_number,
            destination_city=request.destination_city,
            destination_street=request.destination_street,
            destination_house_number=request.destination_house_number,
            origin_address_id=payload.origin_address_id,
            destination_address_id=payload.destination_address_id,
            price_amount=request.price_amount,
            station_id=request.station_id,
            dispatcher_id=payload.current_user.id,
            metadata={"source": "dispatcher", "createdByUserId": payload.current_user.id},
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
            origin_address_id=payload.origin_address_id,
            destination_address_id=payload.destination_address_id,
            price_amount=payload.price,
            metadata={"source": "phone", "callSessionId": payload.payload.call_session_id},
        )
