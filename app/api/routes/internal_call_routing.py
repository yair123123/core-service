from fastapi import APIRouter, Depends

from app.dependencies import get_call_routing_service, get_phone_normalizer
from app.domain.schemas.call_routing import CallRoutingResolveRequest, CallRoutingResolveResponse
from app.services.call_routing_service import CallRoutingService
from app.services.phone_normalizer import PhoneNormalizer

router = APIRouter(prefix="/internal/call-routing", tags=["internal-call-routing"])


@router.post("/resolve", response_model=CallRoutingResolveResponse)
def resolve_call(
    payload: CallRoutingResolveRequest,
    service: CallRoutingService = Depends(get_call_routing_service),
    phone_normalizer: PhoneNormalizer = Depends(get_phone_normalizer),
) -> CallRoutingResolveResponse:
    normalized_phone = phone_normalizer.normalize_israeli_phone(payload.phone)
    return service.resolve(normalized_phone)
