from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DriverProfileModel(Base):
    __tablename__ = "driver_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    can_receive_rides_for_non_payment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("UserModel", back_populates="driver_profile")
    station_links = relationship("DriverProfileStationModel", back_populates="driver_profile", cascade="all, delete-orphan")
    rides = relationship("RideModel", foreign_keys="RideModel.driver_id", back_populates="driver_profile")
