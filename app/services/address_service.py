from dataclasses import dataclass

from app.db.models.address_model import AddressModel
from app.repositories.address_repository import AddressRepository
from app.services.geocoding_client import (
    GeocodeAddressRequestDto,
    GeocodeAddressResponseDto,
    GeocodingClient,
    GeocodingClientError,
)


class AddressResolutionError(Exception):
    pass


@dataclass(slots=True)
class AddressInput:
    city: str
    street: str
    house_number: str
    country_code: str = "IL"


class AddressService:
    def __init__(
        self,
        geocoding_client: GeocodingClient,
        address_repository: AddressRepository,
        required_match_quality: str = "high",
    ) -> None:
        self.geocoding_client = geocoding_client
        self.address_repository = address_repository
        self.required_match_quality = required_match_quality

    def resolve_and_create_address(self, payload: AddressInput) -> AddressModel:
        request = self._to_dto(payload)
        try:
            response = self.geocoding_client.geocode_address(request)
        except GeocodingClientError as exc:
            raise AddressResolutionError("Geocoding service transport failure") from exc
        return self._validate_and_persist(response)

    def resolve_and_create_address_batch(self, origin: AddressInput, destination: AddressInput) -> tuple[AddressModel, AddressModel]:
        requests = [self._to_dto(origin), self._to_dto(destination)]
        try:
            response = self.geocoding_client.geocode_batch(requests)
        except GeocodingClientError as exc:
            raise AddressResolutionError("Geocoding service transport failure") from exc

        if len(response.results) != 2:
            raise AddressResolutionError("Geocoding batch response is incomplete")

        return self._validate_and_persist(response.results[0]), self._validate_and_persist(response.results[1])

    @staticmethod
    def _to_dto(payload: AddressInput) -> GeocodeAddressRequestDto:
        return GeocodeAddressRequestDto(
            city=payload.city,
            street=payload.street,
            house_number=payload.house_number,
            country_code=payload.country_code,
        )

    def _validate_and_persist(self, response: GeocodeAddressResponseDto) -> AddressModel:
        if not response.success:
            detail = response.error or (response.warnings[0] if response.warnings else "Geocoding failed")
            raise AddressResolutionError(detail)
        if response.result is None:
            raise AddressResolutionError("Geocoding did not return a result")
        quality = (response.result.match_quality or "").lower()
        if quality != self.required_match_quality:
            raise AddressResolutionError(f"Geocoding match quality '{quality or 'unknown'}' is not acceptable")

        return self.address_repository.create_address(
            city=response.query.city,
            street=response.query.street,
            house_number=response.query.house_number,
            country_code=response.query.country_code,
            formatted_address=response.result.formatted_address,
            lat=response.result.lat,
            lon=response.result.lon,
            provider=response.result.provider,
            provider_place_id=response.result.provider_place_id,
            match_quality=response.result.match_quality,
            partial_match=bool(response.result.partial_match),
            raw_query_json=response.query.to_payload(),
            warnings_json=response.warnings,
        )
