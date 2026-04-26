from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.enums.ride_status import RideStatus


class RideModel(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)
    driver_id: Mapped[int | None] = mapped_column(ForeignKey("driver_profiles.id"), index=True, nullable=True)
    dispatcher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    station_id: Mapped[int | None] = mapped_column(ForeignKey("stations.id"), index=True, nullable=True)
    origin_address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id"), index=True, nullable=True)
    destination_address_id: Mapped[int | None] = mapped_column(ForeignKey("addresses.id"), index=True, nullable=True)

    origin_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    origin_city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    origin_street: Mapped[str | None] = mapped_column(String(120), nullable=True)
    origin_house_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    destination_city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    destination_street: Mapped[str | None] = mapped_column(String(120), nullable=True)
    destination_house_number: Mapped[str | None] = mapped_column(String(20), nullable=True)

    price_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[RideStatus] = mapped_column(Enum(RideStatus), nullable=False, index=True)
    dispatch_round_number: Mapped[int] = mapped_column(default=0, nullable=False)
    dispatch_current_round_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_dispatch_result_round_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_dispatch_result_status: Mapped[str | None] = mapped_column(String(40), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer = relationship("CustomerModel", back_populates="rides")
    driver_profile = relationship("DriverProfileModel", foreign_keys=[driver_id], back_populates="rides")
    dispatcher = relationship("UserModel", foreign_keys=[dispatcher_id], back_populates="dispatched_rides")
    station = relationship("StationModel", back_populates="rides")
    origin_address = relationship("AddressModel", foreign_keys=[origin_address_id], back_populates="origin_rides")
    destination_address = relationship("AddressModel", foreign_keys=[destination_address_id], back_populates="destination_rides")
    events = relationship("RideEventModel", back_populates="ride")
