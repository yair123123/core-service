from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DispatcherProfileModel(Base):
    __tablename__ = "dispatcher_profile"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

