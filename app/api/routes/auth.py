from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service, get_current_user
from app.domain.schemas.auth import CurrentUserResponse, LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    return auth_service.authenticate(payload.username, payload.password)


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: CurrentUserResponse = Depends(get_current_user)) -> CurrentUserResponse:
    return current_user
