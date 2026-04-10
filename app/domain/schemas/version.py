from pydantic import BaseModel


class VersionInfoResponse(BaseModel):
    service_version: str
    min_supported_app_version: str
    latest_app_version: str
    app_version: str | None = None
    must_update: bool | None = None
    update_url: str | None = None
    update_message: str | None = None
