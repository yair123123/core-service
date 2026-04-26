from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from app.db.models.dispatcher_profile_model import DispatcherProfileModel
from app.db.models.driver_profile_model import DriverProfileModel
from app.db.models.station_owner_profile_model import StationOwnerProfileModel
from app.db.models.user_model import UserModel


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> UserModel | None:
        stmt = self._base_query().where(UserModel.username == username)
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: int) -> UserModel | None:
        stmt = self._base_query().where(UserModel.id == user_id)
        return self.db.scalar(stmt)

    def _base_query(self):
        return select(UserModel).options(
            selectinload(UserModel.driver_profile).selectinload(DriverProfileModel.station_links),
            selectinload(UserModel.dispatcher_profile).selectinload(DispatcherProfileModel.station_links),
            selectinload(UserModel.station_owner_profile).selectinload(StationOwnerProfileModel.station_links),
        )
