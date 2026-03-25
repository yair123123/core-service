from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db_session
from app.repositories.customer_repository import CustomerRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository
from app.services.call_routing_service import CallRoutingService
from app.services.phone_normalizer import PhoneNormalizer
from app.services.pricing_service import PricingService
from app.services.ride_cancellation_service import RideCancellationService
from app.services.ride_confirmation_service import RideConfirmationService
from app.services.ride_order_service import RideOrderService
from app.services.speech_processing_adapter import SpeechProcessingAdapter


def get_customer_repository(db: Session = Depends(get_db_session)) -> CustomerRepository:
    return CustomerRepository(db)


def get_driver_repository(db: Session = Depends(get_db_session)) -> DriverRepository:
    return DriverRepository(db)


def get_ride_repository(db: Session = Depends(get_db_session)) -> RideRepository:
    return RideRepository(db)


def get_ride_event_repository(db: Session = Depends(get_db_session)) -> RideEventRepository:
    return RideEventRepository(db)


def get_phone_normalizer() -> PhoneNormalizer:
    return PhoneNormalizer()


def get_speech_processing_adapter() -> SpeechProcessingAdapter:
    return SpeechProcessingAdapter()


def get_pricing_service(settings: Settings = Depends(get_settings)) -> PricingService:
    return PricingService(fixed_city_ride_price=settings.fixed_city_ride_price)


def get_call_routing_service(
    customer_repository: CustomerRepository = Depends(get_customer_repository),
    driver_repository: DriverRepository = Depends(get_driver_repository),
    ride_repository: RideRepository = Depends(get_ride_repository),
) -> CallRoutingService:
    return CallRoutingService(customer_repository, driver_repository, ride_repository)


def get_ride_order_service(
    customer_repository: CustomerRepository = Depends(get_customer_repository),
    ride_repository: RideRepository = Depends(get_ride_repository),
    ride_event_repository: RideEventRepository = Depends(get_ride_event_repository),
    phone_normalizer: PhoneNormalizer = Depends(get_phone_normalizer),
    speech_processing_adapter: SpeechProcessingAdapter = Depends(get_speech_processing_adapter),
    pricing_service: PricingService = Depends(get_pricing_service),
) -> RideOrderService:
    return RideOrderService(
        customer_repository,
        ride_repository,
        ride_event_repository,
        phone_normalizer,
        speech_processing_adapter,
        pricing_service,
    )


def get_ride_confirmation_service(
    ride_repository: RideRepository = Depends(get_ride_repository),
    ride_event_repository: RideEventRepository = Depends(get_ride_event_repository),
) -> RideConfirmationService:
    return RideConfirmationService(ride_repository, ride_event_repository)


def get_ride_cancellation_service(
    customer_repository: CustomerRepository = Depends(get_customer_repository),
    ride_repository: RideRepository = Depends(get_ride_repository),
    ride_event_repository: RideEventRepository = Depends(get_ride_event_repository),
    phone_normalizer: PhoneNormalizer = Depends(get_phone_normalizer),
) -> RideCancellationService:
    return RideCancellationService(customer_repository, ride_repository, ride_event_repository, phone_normalizer)
