from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RideEventModel(Base):
    __tablename__ = "ride_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[dict[str, Any] | str | None] = mapped_column(JSON().with_variant(Text, "sqlite"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ride = relationship("RideModel", back_populates="events")
