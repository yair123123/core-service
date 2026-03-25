from datetime import datetime

from pydantic import BaseModel


class DriverRead(BaseModel):
    id: int
    phone_number: str
    name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
