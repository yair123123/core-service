from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StationModel(Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    dispatcher_profile_links = relationship("DispatcherProfileStationModel", back_populates="station")
    driver_profile_links = relationship("DriverProfileStationModel", back_populates="station")
    station_owner_profile_links = relationship("StationOwnerProfileStationModel", back_populates="station")
    rides = relationship("RideModel", back_populates="station")
