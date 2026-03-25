from fastapi import APIRouter, Depends

from app.dependencies import get_ride_order_service
from app.domain.schemas.ride_order_processing import ProcessCallOrderRequest, ProcessCallOrderResponse
from app.services.ride_order_service import RideOrderService

router = APIRouter(prefix="/internal/orders", tags=["internal-orders"])


@router.post("/process-call-order", response_model=ProcessCallOrderResponse)
def process_call_order(
    payload: ProcessCallOrderRequest,
    service: RideOrderService = Depends(get_ride_order_service),
) -> ProcessCallOrderResponse:
    return service.process_call_order(payload)
