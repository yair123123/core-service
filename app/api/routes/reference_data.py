from fastapi import APIRouter, Depends

from app.dependencies import get_reference_data_service
from app.domain.schemas.reference_data import (
    AdditionalMessageTemplateResponse,
    CityResponse,
    PriceTemplateResponse,
    ReferenceDataResponse,
)
from app.services.reference_data_service import ReferenceDataService

router = APIRouter(prefix="/reference-data", tags=["reference-data"])


@router.get("", response_model=ReferenceDataResponse)
def get_reference_data_bundle(service: ReferenceDataService = Depends(get_reference_data_service)) -> ReferenceDataResponse:
    return service.get_reference_data_bundle()


@router.get("/cities", response_model=list[CityResponse])
def get_reference_data_cities(service: ReferenceDataService = Depends(get_reference_data_service)) -> list[CityResponse]:
    return service.get_all_cities()


@router.get("/price-templates", response_model=list[PriceTemplateResponse])
def get_reference_data_price_templates(
    service: ReferenceDataService = Depends(get_reference_data_service),
) -> list[PriceTemplateResponse]:
    return service.get_all_price_templates()


@router.get("/additional-message-templates", response_model=list[AdditionalMessageTemplateResponse])
def get_reference_data_additional_message_templates(
    service: ReferenceDataService = Depends(get_reference_data_service),
) -> list[AdditionalMessageTemplateResponse]:
    return service.get_all_additional_message_templates()
