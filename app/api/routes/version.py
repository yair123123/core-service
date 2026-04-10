from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.domain.schemas.version import VersionInfoResponse

router = APIRouter(tags=["version"])


def _parse_version(value: str) -> tuple[int, ...]:
    normalized = value.strip().removeprefix("v")
    parts = normalized.split(".")
    if not parts or any((not part.isdigit()) for part in parts):
        raise ValueError("Version must be numeric and dot-separated (example: 1.2.3)")
    return tuple(int(part) for part in parts)


def _is_version_lower(current: str, minimum: str) -> bool:
    current_parts = _parse_version(current)
    minimum_parts = _parse_version(minimum)
    max_len = max(len(current_parts), len(minimum_parts))
    padded_current = current_parts + (0,) * (max_len - len(current_parts))
    padded_minimum = minimum_parts + (0,) * (max_len - len(minimum_parts))
    return padded_current < padded_minimum


@router.get("/version", response_model=VersionInfoResponse)
def version(app_version: str | None = Query(default=None, description="Client app version, e.g. 1.4.2")) -> VersionInfoResponse:
    settings = get_settings()

    must_update: bool | None = None
    if app_version is not None:
        try:
            must_update = _is_version_lower(app_version, settings.min_supported_app_version)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return VersionInfoResponse(
        service_version=settings.service_version,
        min_supported_app_version=settings.min_supported_app_version,
        latest_app_version=settings.latest_app_version,
        app_version=app_version,
        must_update=must_update,
        update_url=settings.app_update_url,
        update_message=settings.app_update_message,
    )
