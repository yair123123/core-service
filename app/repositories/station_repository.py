from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.station_model import StationModel


class StationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all_stations(self, active_only: bool = True) -> list[StationModel]:
        stmt = select(StationModel)
        if active_only:
            stmt = stmt.where(StationModel.is_active.is_(True))
        return list(self.db.scalars(stmt).all())

    def get_station_by_id(self, station_id: int, active_only: bool = True) -> StationModel | None:
        stmt = select(StationModel).where(StationModel.id == station_id)
        if active_only:
            stmt = stmt.where(StationModel.is_active.is_(True))
        return self.db.scalar(stmt)

    def get_stations_by_ids(self, station_ids: list[int], active_only: bool = True) -> list[StationModel]:
        if not station_ids:
            return []
        stmt = select(StationModel).where(StationModel.id.in_(station_ids))
        if active_only:
            stmt = stmt.where(StationModel.is_active.is_(True))
        return list(self.db.scalars(stmt).all())
