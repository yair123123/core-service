from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    rules: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    dispatcher_station_links = relationship(
        "UserDispatcherStationModel", back_populates="user", cascade="all, delete-orphan"
    )
    driver_station_links = relationship("UserDriverStationModel", back_populates="users", cascade="all, delete-orphan")
    driver_profile = relationship("DriverProfileModel", back_populates="users")
    dispatcher_profile = relationship("DispatcherProfileModel", back_populates="users")
    rides = relationship("RideModel", back_populates="users")
