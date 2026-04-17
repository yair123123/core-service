import pytest
from sqlalchemy import text

from app.repositories.address_repository import AddressRepository
from app.services.address_service import AddressInput, AddressResolutionError, AddressService
from app.services.geocoding_client import (
    GeocodeAddressRequestDto,
    GeocodeAddressResponseDto,
    GeocodeAddressResultDto,
    GeocodeBatchResponseDto,
)


class _FakeGeocodingClient:
    def __init__(self, *, single: GeocodeAddressResponseDto | None = None, batch: GeocodeBatchResponseDto | None = None):
        self.single = single
        self.batch = batch

    def geocode_address(self, payload: GeocodeAddressRequestDto) -> GeocodeAddressResponseDto:
        return self.single  # type: ignore[return-value]

    def geocode_batch(self, addresses: list[GeocodeAddressRequestDto]) -> GeocodeBatchResponseDto:
        return self.batch  # type: ignore[return-value]


def _successful_response(city: str, street: str, house_number: str) -> GeocodeAddressResponseDto:
    return GeocodeAddressResponseDto(
        success=True,
        query=GeocodeAddressRequestDto(city=city, street=street, house_number=house_number, country_code="IL"),
        result=GeocodeAddressResultDto(
            lat=32.1,
            lon=34.8,
            formatted_address=f"{street} {house_number}, {city}",
            provider="mapbox",
            provider_place_id="place.1",
            match_quality="high",
            partial_match=False,
        ),
        warnings=[],
        error=None,
    )


def test_resolve_and_create_address_creates_row(db_session):
    client = _FakeGeocodingClient(single=_successful_response("Tel Aviv", "Herzl", "10"))
    service = AddressService(client, AddressRepository(db_session))

    address = service.resolve_and_create_address(AddressInput(city="Tel Aviv", street="Herzl", house_number="10"))

    assert address.id is not None
    assert address.match_quality == "high"
    assert address.raw_query_json["city"] == "Tel Aviv"


def test_resolve_and_create_address_batch_creates_two_rows(db_session):
    batch = GeocodeBatchResponseDto(
        success=True,
        results=[
            _successful_response("Tel Aviv", "Herzl", "10"),
            _successful_response("Tel Aviv", "Allenby", "5"),
        ],
        warnings=[],
        error=None,
    )
    client = _FakeGeocodingClient(batch=batch)
    service = AddressService(client, AddressRepository(db_session))

    origin, destination = service.resolve_and_create_address_batch(
        AddressInput(city="Tel Aviv", street="Herzl", house_number="10"),
        AddressInput(city="Tel Aviv", street="Allenby", house_number="5"),
    )

    assert origin.id is not None
    assert destination.id is not None
    assert origin.id != destination.id


def test_failed_geocode_does_not_create_row(db_session):
    failed = GeocodeAddressResponseDto(
        success=False,
        query=GeocodeAddressRequestDto(city="Tel Aviv", street="Herzl", house_number="10", country_code="IL"),
        result=None,
        warnings=["No geocoding result found"],
        error=None,
    )
    client = _FakeGeocodingClient(single=failed)
    service = AddressService(client, AddressRepository(db_session))

    with pytest.raises(AddressResolutionError):
        service.resolve_and_create_address(AddressInput(city="Tel Aviv", street="Herzl", house_number="10"))

    assert db_session.execute(text("SELECT COUNT(*) FROM addresses")).scalar_one() == 0


def test_medium_quality_is_rejected(db_session):
    medium = GeocodeAddressResponseDto(
        success=True,
        query=GeocodeAddressRequestDto(city="Tel Aviv", street="Herzl", house_number="10", country_code="IL"),
        result=GeocodeAddressResultDto(
            lat=32.1,
            lon=34.8,
            formatted_address="Herzl 10, Tel Aviv",
            provider="mapbox",
            provider_place_id="place.1",
            match_quality="medium",
            partial_match=True,
        ),
        warnings=[],
        error=None,
    )
    client = _FakeGeocodingClient(single=medium)
    service = AddressService(client, AddressRepository(db_session))

    with pytest.raises(AddressResolutionError):
        service.resolve_and_create_address(AddressInput(city="Tel Aviv", street="Herzl", house_number="10"))
