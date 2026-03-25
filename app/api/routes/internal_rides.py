from fastapi import APIRouter, Depends

from app.dependencies import get_ride_cancellation_service, get_ride_confirmation_service
from app.domain.schemas.ride_confirmation import CancelSearchingRideResponse, ConfirmRideResponse
from app.services.ride_cancellation_service import RideCancellationService
from app.services.ride_confirmation_service import RideConfirmationService

router = APIRouter(prefix="/internal/rides", tags=["internal-rides"])


@router.post("/{ride_id}/confirm", response_model=ConfirmRideResponse)
def confirm_ride(
    ride_id: int,
    service: RideConfirmationService = Depends(get_ride_confirmation_service),
) -> ConfirmRideResponse:
    return service.confirm_ride(ride_id)


@router.post("/by-customer/{phone}/cancel-searching", response_model=CancelSearchingRideResponse)
def cancel_searching(
    phone: str,
    service: RideCancellationService = Depends(get_ride_cancellation_service),
) -> CancelSearchingRideResponse:
    return service.cancel_searching_ride(phone)
