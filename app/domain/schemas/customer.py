from datetime import datetime

from pydantic import BaseModel


class CustomerRead(BaseModel):
    id: int
    phone_number: str
    created_at: datetime
    updated_at: datetime
