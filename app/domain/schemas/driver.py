from datetime import datetime

from pydantic import BaseModel


class DriverRead(BaseModel):
    id: int
    user_id: int
    phone_number: str | None
    display_name: str | None
    gender: str | None
    rating: float | None
    can_receive_rides_for_non_payment: bool
    created_at: datetime
    updated_at: datetime
