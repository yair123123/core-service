import httpx

from app.domain.schemas.dispatch import StartDispatchRoundRequest


class DispatchSocketClient:
    def __init__(self, base_url: str, internal_service_secret: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.internal_service_secret = internal_service_secret

    def start_round(self, payload: StartDispatchRoundRequest) -> None:
        response = httpx.post(
            f"{self.base_url}/internal/dispatch/start-round",
            json=payload.model_dump(mode="json", by_alias=True),
            headers={"X-Internal-Secret": self.internal_service_secret},
            timeout=5.0,
        )
        response.raise_for_status()
