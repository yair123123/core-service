from typing import Any

from sqlalchemy.orm import Session

from app.db.models.ride_event_model import RideEventModel


class RideEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_event(self, ride_id: int, event_type: str, payload_json: dict[str, Any] | None = None) -> RideEventModel:
        event = RideEventModel(ride_id=ride_id, event_type=event_type, payload_json=payload_json)
        self.db.add(event)
        self.db.flush()
        return event
