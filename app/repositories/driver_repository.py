from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.driver_model import DriverModel


class DriverRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_phone(self, phone_number: str) -> DriverModel | None:
        stmt = select(DriverModel).where(DriverModel.phone_number == phone_number)
        return self.db.scalar(stmt)

    def get_by_id(self, driver_id: int) -> DriverModel | None:
        return self.db.get(DriverModel, driver_id)
