from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums.ride_status import RideStatus


class RideRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    driver_id: int | None
    station_id: int | None
    status: RideStatus
    created_at: datetime
