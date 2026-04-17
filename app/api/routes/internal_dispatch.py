from fastapi import APIRouter, Depends

from app.dependencies import get_dispatch_round_orchestration_service, verify_internal_service_secret
from app.domain.schemas.dispatch import DispatchRoundResultRequest, DispatchRoundResultResponse
from app.services.dispatch_round_orchestration_service import DispatchRoundOrchestrationService

router = APIRouter(prefix="/internal/dispatch", tags=["internal-dispatch"])


@router.post("/round-result", response_model=DispatchRoundResultResponse, dependencies=[Depends(verify_internal_service_secret)])
def consume_round_result(
    payload: DispatchRoundResultRequest,
    service: DispatchRoundOrchestrationService = Depends(get_dispatch_round_orchestration_service),
) -> DispatchRoundResultResponse:
    return service.handle_round_result(payload)
