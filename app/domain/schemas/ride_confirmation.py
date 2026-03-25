from pydantic import BaseModel


class ConfirmRideResponse(BaseModel):
    success: bool


class CancelSearchingRideResponse(BaseModel):
    success: bool
