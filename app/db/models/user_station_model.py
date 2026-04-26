from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DispatcherProfileStationModel(Base):
    __tablename__ = "dispatcher_profile_stations"

    dispatcher_profile_id: Mapped[int] = mapped_column(
        ForeignKey("dispatcher_profiles.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), primary_key=True, index=True)

    dispatcher_profile = relationship("DispatcherProfileModel", back_populates="station_links")
    station = relationship("StationModel", back_populates="dispatcher_profile_links")


class DriverProfileStationModel(Base):
    __tablename__ = "driver_profile_stations"

    driver_profile_id: Mapped[int] = mapped_column(
        ForeignKey("driver_profiles.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), primary_key=True, index=True)

    driver_profile = relationship("DriverProfileModel", back_populates="station_links")
    station = relationship("StationModel", back_populates="driver_profile_links")


class StationOwnerProfileStationModel(Base):
    __tablename__ = "station_owner_profile_stations"

    station_owner_profile_id: Mapped[int] = mapped_column(
        ForeignKey("station_owner_profiles.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), primary_key=True, index=True)

    station_owner_profile = relationship("StationOwnerProfileModel", back_populates="station_links")
    station = relationship("StationModel", back_populates="station_owner_profile_links")
