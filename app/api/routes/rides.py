from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_ride_service
from app.domain.schemas.auth import CurrentUserResponse
from app.domain.schemas.ride import RideRead
from app.services.ride_service import RideService

router = APIRouter(prefix="/rides", tags=["rides"])


@router.get("/my-driver-rides", response_model=list[RideRead])
def get_my_driver_rides(
    current_user: CurrentUserResponse = Depends(get_current_user),
    service: RideService = Depends(get_ride_service),
) -> list[RideRead]:
    return service.get_my_driver_rides(current_user)
