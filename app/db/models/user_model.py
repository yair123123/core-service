from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20), unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rules: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    driver_profile = relationship(
        "DriverProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    dispatcher_profile = relationship(
        "DispatcherProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    station_owner_profile = relationship(
        "StationOwnerProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    dispatched_rides = relationship("RideModel", foreign_keys="RideModel.dispatcher_id", back_populates="dispatcher")
