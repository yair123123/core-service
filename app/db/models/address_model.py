from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AddressModel(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    city: Mapped[str] = mapped_column(String(80), nullable=False)
    street: Mapped[str] = mapped_column(String(120), nullable=False)
    house_number: Mapped[str] = mapped_column(String(20), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)

    formatted_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    provider_place_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    match_quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    partial_match: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    raw_query_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    warnings_json: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    origin_rides = relationship("RideModel", foreign_keys="RideModel.origin_address_id", back_populates="origin_address")
    destination_rides = relationship(
        "RideModel", foreign_keys="RideModel.destination_address_id", back_populates="destination_address"
    )
