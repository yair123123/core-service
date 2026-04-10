from fastapi import HTTPException, status

from app.db.models.station_model import StationModel
from app.domain.schemas.station import StationResponse
from app.repositories.station_repository import StationRepository


class StationService:
    def __init__(self, station_repository: StationRepository) -> None:
        self.station_repository = station_repository

    def get_all(self) -> list[StationResponse]:
        stations = self.station_repository.get_all_stations()
        return [self._to_response(station) for station in stations]

    def get_by_id(self, station_id: int) -> StationResponse:
        station = self.station_repository.get_station_by_id(station_id)
        if station is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
        return self._to_response(station)

    def get_by_ids(self, station_ids: list[int]) -> list[StationResponse]:
        stations = self.station_repository.get_stations_by_ids(station_ids)
        return [self._to_response(station) for station in stations]

    def _to_response(self, station: StationModel) -> StationResponse:
        return StationResponse(id=station.id, name=station.name, isActive=station.is_active)
