from sqlalchemy.orm import Session

from app.db.models.address_model import AddressModel


class AddressRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_address(
        self,
        *,
        city: str,
        street: str,
        house_number: str,
        country_code: str,
        formatted_address: str | None,
        lat: float,
        lon: float,
        provider: str | None,
        provider_place_id: str | None,
        match_quality: str | None,
        partial_match: bool,
        raw_query_json: dict | None,
        warnings_json: list[str] | None,
    ) -> AddressModel:
        address = AddressModel(
            city=city,
            street=street,
            house_number=house_number,
            country_code=country_code,
            formatted_address=formatted_address,
            lat=lat,
            lon=lon,
            provider=provider,
            provider_place_id=provider_place_id,
            match_quality=match_quality,
            partial_match=partial_match,
            raw_query_json=raw_query_json,
            warnings_json=warnings_json,
        )
        self.db.add(address)
        self.db.flush()
        return address
