from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "core-service"
    environment: str = "dev"
    database_url: str = "postgresql://postgres:1234@localhost:5432/taxi_db"
    fixed_city_ride_price: float = Field(default=25.0, gt=0)
    service_version: str = "1.0.0"
    min_supported_app_version: str = "1.0.0"
    latest_app_version: str = "1.0.0"
    app_update_url: str | None = None
    app_update_message: str = "A newer app version is available."
    auth_jwt_secret: str = "change-me"
    auth_jwt_algorithm: str = "HS256"
    auth_access_token_expires_in_seconds: int = Field(default=3600, gt=0)
    dispatch_socket_base_url: str = "http://dispatch-socket-service:8000"
    geocoding_base_url: str = "http://geocoding-service:8000"
    geocoding_timeout_seconds: float = Field(default=5.0, gt=0)
    internal_service_secret: str = "change-me-internal"
    dispatch_round_1_radius_km: float = Field(default=2.0, gt=0)
    dispatch_round_1_timeout_seconds: int = Field(default=15, gt=0)
    dispatch_round_1_max_candidates: int = Field(default=5, gt=0)
    dispatch_round_2_radius_km: float = Field(default=5.0, gt=0)
    dispatch_round_2_timeout_seconds: int = Field(default=20, gt=0)
    dispatch_round_2_max_candidates: int = Field(default=8, gt=0)
    dispatch_round_3_radius_km: float = Field(default=10.0, gt=0)
    dispatch_round_3_timeout_seconds: int = Field(default=25, gt=0)
    dispatch_round_3_max_candidates: int = Field(default=12, gt=0)

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CORE_SERVICE_", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
