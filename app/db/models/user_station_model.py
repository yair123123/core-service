from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserDispatcherStationModel(Base):
    __tablename__ = "user_dispatcher_stations"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), primary_key=True, index=True)

    user = relationship("UserModel", back_populates="dispatcher_station_links")
    station = relationship("StationModel", back_populates="dispatcher_user_links")


class UserDriverStationModel(Base):
    __tablename__ = "user_driver_stations"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id", ondelete="CASCADE"), primary_key=True, index=True)

    user = relationship("UserModel", back_populates="driver_station_links")
    station = relationship("StationModel", back_populates="driver_user_links")
