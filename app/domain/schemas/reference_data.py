from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CityResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    is_active: bool = Field(alias="isActive")


class PriceTemplateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    value: Decimal
    is_active: bool = Field(alias="isActive")


class AdditionalMessageTemplateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    text: str
    is_active: bool = Field(alias="isActive")


class ReferenceDataResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    cities: list[CityResponse]
    price_templates: list[PriceTemplateResponse] = Field(alias="priceTemplates")
    additional_message_templates: list[AdditionalMessageTemplateResponse] = Field(alias="additionalMessageTemplates")
