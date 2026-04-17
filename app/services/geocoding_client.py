from dataclasses import dataclass

import httpx


class GeocodingClientError(Exception):
    pass


@dataclass(slots=True)
class GeocodeAddressRequestDto:
    city: str
    street: str
    house_number: str
    country_code: str

    def to_payload(self) -> dict[str, str]:
        return {
            "city": self.city,
            "street": self.street,
            "house_number": self.house_number,
            "country_code": self.country_code,
        }


@dataclass(slots=True)
class GeocodeAddressResultDto:
    lat: float
    lon: float
    formatted_address: str | None
    provider: str | None
    provider_place_id: str | None
    match_quality: str | None
    partial_match: bool | None


@dataclass(slots=True)
class GeocodeAddressResponseDto:
    success: bool
    query: GeocodeAddressRequestDto
    result: GeocodeAddressResultDto | None
    warnings: list[str]
    error: str | None


@dataclass(slots=True)
class GeocodeBatchResponseDto:
    success: bool
    results: list[GeocodeAddressResponseDto]
    warnings: list[str]
    error: str | None


class GeocodingClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def geocode_address(self, payload: GeocodeAddressRequestDto) -> GeocodeAddressResponseDto:
        data = self._post_json("/v1/geocode/address", {"city": payload.city, "street": payload.street, "house_number": payload.house_number, "country_code": payload.country_code})
        return self._parse_item(data)

    def geocode_batch(self, addresses: list[GeocodeAddressRequestDto]) -> GeocodeBatchResponseDto:
        data = self._post_json("/v1/geocode/batch", {"addresses": [item.to_payload() for item in addresses]})
        raw_results = data.get("results") or []
        return GeocodeBatchResponseDto(
            success=bool(data.get("success", False)),
            results=[self._parse_item(item) for item in raw_results],
            warnings=self._as_str_list(data.get("warnings")),
            error=data.get("error"),
        )

    def _post_json(self, path: str, payload: dict) -> dict:
        try:
            response = httpx.post(f"{self.base_url}{path}", json=payload, timeout=self.timeout_seconds)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GeocodingClientError("Failed to call geocoding service") from exc

    def _parse_item(self, data: dict) -> GeocodeAddressResponseDto:
        query = data.get("query") or {}
        result_data = data.get("result")
        result = None
        if isinstance(result_data, dict):
            result = GeocodeAddressResultDto(
                lat=float(result_data["lat"]),
                lon=float(result_data["lon"]),
                formatted_address=result_data.get("formatted_address"),
                provider=result_data.get("provider"),
                provider_place_id=result_data.get("provider_place_id"),
                match_quality=result_data.get("match_quality"),
                partial_match=result_data.get("partial_match"),
            )
        return GeocodeAddressResponseDto(
            success=bool(data.get("success", False)),
            query=GeocodeAddressRequestDto(
                city=str(query.get("city") or ""),
                street=str(query.get("street") or ""),
                house_number=str(query.get("house_number") or ""),
                country_code=str(query.get("country_code") or ""),
            ),
            result=result,
            warnings=self._as_str_list(data.get("warnings")),
            error=data.get("error"),
        )

    @staticmethod
    def _as_str_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value]
