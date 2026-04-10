from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    refresh_token: str | None = Field(default=None, alias="refreshToken")
    expires_in: int | None = Field(default=None, alias="expiresIn")


class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    username: str
    gender: str | None = None
    rating: float | None = None
    can_receive_rides_for_non_payment: bool = Field(alias="canReceiveRidesForNonPayment")
    is_dispatcher: bool = Field(alias="isDispatcher")
    dispatcher_stations_id: list[int] = Field(default_factory=list, alias="dispatcherStationsId")
    driver_stations_id: list[int] = Field(default_factory=list, alias="driverStationsId")
