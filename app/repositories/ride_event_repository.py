import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models.ride_event_model import RideEventModel


class RideEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_event(self, ride_id: int, event_type: str, payload_json: dict[str, Any] | None = None) -> RideEventModel:
        payload_value: dict[str, Any] | str | None = payload_json
        if payload_json is not None and self.db.bind is not None and self.db.bind.dialect.name == "sqlite":
            payload_value = json.dumps(payload_json)

        event = RideEventModel(ride_id=ride_id, event_type=event_type, payload_json=payload_value)
        self.db.add(event)
        self.db.flush()
        return event
