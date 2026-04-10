from pydantic import BaseModel, ConfigDict, Field


class StationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    name: str
    is_active: bool = Field(alias="isActive")


class StationByIdsRequest(BaseModel):
    ids: list[int]
