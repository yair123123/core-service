from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class DispatchRoundResultStatus(StrEnum):
    WINNER_SELECTED = "winner_selected"
    NO_CANDIDATES = "no_candidates"
    NO_ACCEPT = "no_accept"
    ROUND_EXPIRED = "round_expired"
    DISPATCH_FAILED = "dispatch_failed"


class DispatchRidePreview(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    origin_text: str | None = Field(default=None, alias="originText")
    destination_text: str | None = Field(default=None, alias="destinationText")
    price: float | None = None
    note: str | None = None


class StartDispatchRoundRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ride_id: int = Field(alias="rideId")
    round_id: str = Field(alias="roundId")
    round_number: int = Field(alias="roundNumber")
    station_id: int | None = Field(default=None, alias="stationId")
    origin_lat: float | None = Field(default=None, alias="originLat")
    origin_lon: float | None = Field(default=None, alias="originLon")
    radius_km: float = Field(alias="radiusKm")
    timeout_seconds: int = Field(alias="timeoutSeconds")
    max_candidates: int = Field(alias="maxCandidates")
    ride_preview: DispatchRidePreview = Field(alias="ridePreview")


class DispatchRoundResultRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ride_id: int = Field(alias="rideId")
    round_id: str = Field(alias="roundId")
    round_number: int = Field(alias="roundNumber")
    status: DispatchRoundResultStatus
    winner_driver_id: int | None = Field(default=None, alias="winnerDriverId")


class DispatchRoundResultResponse(BaseModel):
    success: bool
    action: str
