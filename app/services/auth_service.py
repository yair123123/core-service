from fastapi import HTTPException, status

from app.config import Settings
from app.db.models.user_model import UserModel
from app.domain.schemas.auth import CurrentUserResponse, LoginResponse
from app.repositories.user_repository import UserRepository
from app.services.security import create_access_token, verify_password


class AuthService:
    def __init__(self, user_repository: UserRepository, settings: Settings) -> None:
        self.user_repository = user_repository
        self.settings = settings

    def authenticate(self, username: str, password: str) -> LoginResponse:
        user = self.user_repository.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

        access_token = create_access_token(
            user_id=user.id,
            secret_key=self.settings.auth_jwt_secret,
            algorithm=self.settings.auth_jwt_algorithm,
            expires_in_seconds=self.settings.auth_access_token_expires_in_seconds,
        )
        return LoginResponse(
            accessToken=access_token,
            refreshToken=None,
            expiresIn=self.settings.auth_access_token_expires_in_seconds,
        )

    def to_current_user_response(self, user: UserModel) -> CurrentUserResponse:
        dispatcher_station_ids = (
            [link.station_id for link in user.dispatcher_station_links]
            if user.dispatcher_station_links
            else user.dispatcher_stations_id
        )
        driver_station_ids = (
            [link.station_id for link in user.driver_station_links] if user.driver_station_links else user.driver_stations_id
        )
        return CurrentUserResponse(
            id=user.id,
            username=user.username,
            gender=user.gender,
            rating=user.rating,
            canReceiveRidesForNonPayment=user.can_receive_rides_for_non_payment,
            isDispatcher=user.is_dispatcher,
            dispatcherStationsId=dispatcher_station_ids,
            driverStationsId=driver_station_ids,
        )
