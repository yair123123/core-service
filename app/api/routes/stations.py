from fastapi import APIRouter, Depends

from app.dependencies import get_station_service
from app.domain.schemas.station import StationByIdsRequest, StationResponse
from app.services.station_service import StationService

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("", response_model=list[StationResponse])
def get_stations(service: StationService = Depends(get_station_service)) -> list[StationResponse]:
    return service.get_all()


@router.get("/{station_id}", response_model=StationResponse)
def get_station(station_id: int, service: StationService = Depends(get_station_service)) -> StationResponse:
    return service.get_by_id(station_id)


@router.post("/by-ids", response_model=list[StationResponse])
def get_stations_by_ids(
    payload: StationByIdsRequest,
    service: StationService = Depends(get_station_service),
) -> list[StationResponse]:
    return service.get_by_ids(payload.ids)
