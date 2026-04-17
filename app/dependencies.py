from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db_session
from app.repositories.customer_repository import CustomerRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.reference_data_repository import ReferenceDataRepository
from app.repositories.ride_event_repository import RideEventRepository
from app.repositories.ride_repository import RideRepository
from app.repositories.station_repository import StationRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.call_routing_service import CallRoutingService
from app.services.dispatcher_ride_service import DispatcherRideService
from app.services.dispatch_round_orchestration_service import DispatchRoundOrchestrationService
from app.services.dispatch_round_policy_service import DispatchRoundPolicyService
from app.services.dispatch_socket_client import DispatchSocketClient
from app.services.phone_normalizer import PhoneNormalizer
from app.services.pricing_service import PricingService
from app.services.ride_cancellation_service import RideCancellationService
from app.services.ride_command_builders import DispatcherRideCommandBuilder, PhoneRideCommandBuilder
from app.services.ride_creation_service import RideCreationService
from app.services.reference_data_service import ReferenceDataService
from app.services.ride_confirmation_service import RideConfirmationService
from app.services.ride_order_service import RideOrderService
from app.services.ride_service import RideService
from app.services.security import decode_token
from app.services.station_service import StationService
from app.services.speech_processing_adapter import SpeechProcessingAdapter
from app.domain.schemas.auth import CurrentUserResponse

http_bearer = HTTPBearer(auto_error=False)


def get_customer_repository(db: Session = Depends(get_db_session)) -> CustomerRepository:
    return CustomerRepository(db)


def get_driver_repository(db: Session = Depends(get_db_session)) -> DriverRepository:
    return DriverRepository(db)


def get_ride_repository(db: Session = Depends(get_db_session)) -> RideRepository:
    return RideRepository(db)


def get_ride_event_repository(db: Session = Depends(get_db_session)) -> RideEventRepository:
    return RideEventRepository(db)


def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db)


def get_station_repository(db: Session = Depends(get_db_session)) -> StationRepository:
    return StationRepository(db)


def get_reference_data_repository(db: Session = Depends(get_db_session)) -> ReferenceDataRepository:
    return ReferenceDataRepository(db)


def get_phone_normalizer() -> PhoneNormalizer:
    return PhoneNormalizer()


def get_speech_processing_adapter() -> SpeechProcessingAdapter:
    return SpeechProcessingAdapter()


def get_pricing_service(settings: Settings = Depends(get_settings)) -> PricingService:
    return PricingService(fixed_city_ride_price=settings.fixed_city_ride_price)


def get_dispatcher_ride_command_builder() -> DispatcherRideCommandBuilder:
    return DispatcherRideCommandBuilder()


def get_phone_ride_command_builder() -> PhoneRideCommandBuilder:
    return PhoneRideCommandBuilder()


def get_dispatch_socket_client(settings: Settings = Depends(get_settings)) -> DispatchSocketClient:
    return DispatchSocketClient(
        base_url=settings.dispatch_socket_base_url,
        internal_service_secret=settings.internal_service_secret,
    )


def get_dispatch_round_policy_service(settings: Settings = Depends(get_settings)) -> DispatchRoundPolicyService:
    return DispatchRoundPolicyService(settings)


def get_dispatch_round_orchestration_service(
    ride_repository: RideRepository = Depends(get_ride_repository),
    ride_event_repository: RideEventRepository = Depends(get_ride_event_repository),
    policy_service: DispatchRoundPolicyService = Depends(get_dispatch_round_policy_service),
    dispatch_socket_client: DispatchSocketClient = Depends(get_dispatch_socket_client),
) -> DispatchRoundOrchestrationService:
    return DispatchRoundOrchestrationService(
        ride_repository=ride_repository,
        ride_event_repository=ride_event_repository,
        policy_service=policy_service,
        dispatch_socket_client=dispatch_socket_client,
    )


def get_ride_creation_service(
    ride_repository: RideRepository = Depends(get_ride_repository),
    ride_event_repository: RideEventRepository = Depends(get_ride_event_repository),
    dispatch_round_orchestration_service: DispatchRoundOrchestrationService = Depends(
        get_dispatch_round_orchestration_service
    ),
) -> RideCreationService:
    return RideCreationService(ride_repository, ride_event_repository, dispatch_round_orchestration_service)


def get_call_routing_service(
    customer_repository: CustomerRepository = Depends(get_customer_repository),
    driver_repository: DriverRepository = Depends(get_driver_repository),
    ride_repository: RideRepository = Depends(get_ride_repository),
) -> CallRoutingService:
    return CallRoutingService(customer_repository, driver_repository, ride_repository)


def get_ride_order_service(
    customer_repository: CustomerRepository = Depends(get_customer_repository),
    ride_repository: RideRepository = Depends(get_ride_repository),
    phone_normalizer: PhoneNormalizer = Depends(get_phone_normalizer),
    speech_processing_adapter: SpeechProcessingAdapter = Depends(get_speech_processing_adapter),
    pricing_service: PricingService = Depends(get_pricing_service),
    phone_command_builder: PhoneRideCommandBuilder = Depends(get_phone_ride_command_builder),
    ride_creation_service: RideCreationService = Depends(get_ride_creation_service),
) -> RideOrderService:
    return RideOrderService(
        customer_repository,
        ride_repository,
        phone_normalizer,
        speech_processing_adapter,
        pricing_service,
        phone_command_builder,
        ride_creation_service,
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


def get_ride_service(
    ride_repository: RideRepository = Depends(get_ride_repository),
) -> RideService:
    return RideService(ride_repository)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(user_repository, settings)


def get_station_service(
    station_repository: StationRepository = Depends(get_station_repository),
) -> StationService:
    return StationService(station_repository)


def get_reference_data_service(
    reference_data_repository: ReferenceDataRepository = Depends(get_reference_data_repository),
) -> ReferenceDataService:
    return ReferenceDataService(reference_data_repository)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    user_repository: UserRepository = Depends(get_user_repository),
    settings: Settings = Depends(get_settings),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserResponse:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = credentials.credentials
    try:
        payload = decode_token(
            token=token,
            secret_key=settings.auth_jwt_secret,
            algorithm=settings.auth_jwt_algorithm,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    subject = payload.get("sub")
    if subject is None or not str(subject).isdigit():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = user_repository.get_by_id(int(subject))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    return auth_service.to_current_user_response(user)


def get_dispatcher_ride_service(
    customer_repository: CustomerRepository = Depends(get_customer_repository),
    phone_normalizer: PhoneNormalizer = Depends(get_phone_normalizer),
    dispatcher_command_builder: DispatcherRideCommandBuilder = Depends(get_dispatcher_ride_command_builder),
    ride_creation_service: RideCreationService = Depends(get_ride_creation_service),
) -> DispatcherRideService:
    return DispatcherRideService(customer_repository, phone_normalizer, dispatcher_command_builder, ride_creation_service)


def verify_internal_service_secret(
    x_internal_secret: str | None = Header(default=None, alias="X-Internal-Secret"),
    settings: Settings = Depends(get_settings),
) -> None:
    if x_internal_secret != settings.internal_service_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid internal secret")
