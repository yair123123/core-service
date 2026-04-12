from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.additional_message_template_model import AdditionalMessageTemplateModel
from app.db.models.city_model import CityModel
from app.db.models.price_template_model import PriceTemplateModel


class ReferenceDataRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all_cities(self, active_only: bool = True) -> list[CityModel]:
        stmt = select(CityModel)
        if active_only:
            stmt = stmt.where(CityModel.is_active.is_(True))
        return list(self.db.scalars(stmt).all())

    def get_all_price_templates(self, active_only: bool = True) -> list[PriceTemplateModel]:
        stmt = select(PriceTemplateModel)
        if active_only:
            stmt = stmt.where(PriceTemplateModel.is_active.is_(True))
        return list(self.db.scalars(stmt).all())

    def get_all_additional_message_templates(self, active_only: bool = True) -> list[AdditionalMessageTemplateModel]:
        stmt = select(AdditionalMessageTemplateModel)
        if active_only:
            stmt = stmt.where(AdditionalMessageTemplateModel.is_active.is_(True))
        return list(self.db.scalars(stmt).all())

    def get_reference_data_bundle(self, active_only: bool = True) -> tuple[
        list[CityModel],
        list[PriceTemplateModel],
        list[AdditionalMessageTemplateModel],
    ]:
        return (
            self.get_all_cities(active_only=active_only),
            self.get_all_price_templates(active_only=active_only),
            self.get_all_additional_message_templates(active_only=active_only),
        )
