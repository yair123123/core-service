from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.driver_profile_model import DriverProfileModel


class DriverRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_phone(self, phone_number: str) -> DriverProfileModel | None:
        stmt = select(DriverProfileModel).where(DriverProfileModel.phone_number == phone_number)
        return self.db.scalar(stmt)

    def get_by_id(self, driver_id: int) -> DriverProfileModel | None:
        return self.db.get(DriverProfileModel, driver_id)
