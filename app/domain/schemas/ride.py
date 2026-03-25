from datetime import datetime

from pydantic import BaseModel

from app.domain.enums.ride_status import RideStatus


class RideRead(BaseModel):
    id: int
    customer_id: int
    driver_id: int | None
    status: RideStatus
    created_at: datetime
