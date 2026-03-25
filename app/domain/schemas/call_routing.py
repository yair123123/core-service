from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.routing_action import RoutingAction


class CallRoutingResolveRequest(BaseModel):
    phone: str


class CallRoutingResolveResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    action: RoutingAction
    ride_id: int | None = Field(default=None, alias="rideId")
    target_phone: str | None = Field(default=None, alias="targetPhone")
    message: str | None = None
