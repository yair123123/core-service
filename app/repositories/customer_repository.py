from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.customer_model import CustomerModel


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_phone(self, phone_number: str) -> CustomerModel | None:
        return self.db.scalar(select(CustomerModel).where(CustomerModel.phone_number == phone_number))

    def get_or_create_by_phone(self, phone_number: str) -> CustomerModel:
        customer = self.get_by_phone(phone_number)
        if customer:
            return customer
        customer = CustomerModel(phone_number=phone_number)
        self.db.add(customer)
        self.db.flush()
        return customer
