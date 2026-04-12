from app.db.models.additional_message_template_model import AdditionalMessageTemplateModel
from app.db.models.city_model import CityModel
from app.db.models.price_template_model import PriceTemplateModel
from app.domain.schemas.reference_data import (
    AdditionalMessageTemplateResponse,
    CityResponse,
    PriceTemplateResponse,
    ReferenceDataResponse,
)
from app.repositories.reference_data_repository import ReferenceDataRepository


class ReferenceDataService:
    def __init__(self, reference_data_repository: ReferenceDataRepository) -> None:
        self.reference_data_repository = reference_data_repository

    def get_all_cities(self, active_only: bool = True) -> list[CityResponse]:
        cities = self.reference_data_repository.get_all_cities(active_only=active_only)
        return [self._to_city_response(city) for city in cities]

    def get_all_price_templates(self, active_only: bool = True) -> list[PriceTemplateResponse]:
        templates = self.reference_data_repository.get_all_price_templates(active_only=active_only)
        return [self._to_price_template_response(template) for template in templates]

    def get_all_additional_message_templates(self, active_only: bool = True) -> list[AdditionalMessageTemplateResponse]:
        templates = self.reference_data_repository.get_all_additional_message_templates(active_only=active_only)
        return [self._to_additional_message_template_response(template) for template in templates]

    def get_reference_data_bundle(self, active_only: bool = True) -> ReferenceDataResponse:
        cities, price_templates, additional_message_templates = self.reference_data_repository.get_reference_data_bundle(
            active_only=active_only
        )
        return ReferenceDataResponse(
            cities=[self._to_city_response(city) for city in cities],
            priceTemplates=[self._to_price_template_response(template) for template in price_templates],
            additionalMessageTemplates=[
                self._to_additional_message_template_response(template) for template in additional_message_templates
            ],
        )

    def _to_city_response(self, city: CityModel) -> CityResponse:
        return CityResponse(id=city.id, name=city.name, isActive=city.is_active)

    def _to_price_template_response(self, template: PriceTemplateModel) -> PriceTemplateResponse:
        return PriceTemplateResponse(
            id=template.id,
            name=template.name,
            value=template.value,
            isActive=template.is_active,
        )

    def _to_additional_message_template_response(
        self, template: AdditionalMessageTemplateModel
    ) -> AdditionalMessageTemplateResponse:
        return AdditionalMessageTemplateResponse(id=template.id, text=template.text, isActive=template.is_active)
