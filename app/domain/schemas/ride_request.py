from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CreateRideFromDispatcherRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_phone: str = Field(alias="customerPhone")
    station_id: int = Field(alias="stationId")
    origin_text: str | None = Field(default=None, alias="originText")
    destination_text: str | None = Field(default=None, alias="destinationText")
    notes_text: str | None = Field(default=None, alias="notesText")
    origin_city: str = Field(alias="originCity")
    origin_street: str = Field(alias="originStreet")
    origin_house_number: str = Field(alias="originHouseNumber")
    destination_city: str = Field(alias="destinationCity")
    destination_street: str = Field(alias="destinationStreet")
    destination_house_number: str = Field(alias="destinationHouseNumber")
    price_amount: Decimal | float | None = Field(default=None, alias="priceAmount")


class CreateRideResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    status: str
