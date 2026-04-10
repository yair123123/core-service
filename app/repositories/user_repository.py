from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.user_model import UserModel


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.username == username)
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: int) -> UserModel | None:
        return self.db.get(UserModel, user_id)
