from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_dispatcher_ride_service, get_ride_service
from app.domain.schemas.auth import CurrentUserResponse
from app.domain.schemas.ride import RideRead
from app.domain.schemas.ride_request import CreateRideFromDispatcherRequest, CreateRideResponse
from app.services.dispatcher_ride_service import DispatcherRideService
from app.services.ride_service import RideService

router = APIRouter(prefix="/rides", tags=["rides"])


@router.post("", response_model=CreateRideResponse)
def create_ride(
    payload: CreateRideFromDispatcherRequest,
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: DispatcherRideService = Depends(get_dispatcher_ride_service),
) -> CreateRideResponse:
    ride = service.create_ride(payload=payload, current_user=current_user)
    return CreateRideResponse(id=ride.id, status=ride.status.value)


@router.get("/my-driver-rides", response_model=list[RideRead])
def get_my_driver_rides(
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: RideService = Depends(get_ride_service),
) -> list[RideRead]:
    return service.get_my_driver_rides(current_user)
