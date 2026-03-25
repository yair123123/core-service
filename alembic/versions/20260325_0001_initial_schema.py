"""initial schema

Revision ID: 20260325_0001
Revises: 
Create Date: 2026-03-25 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260325_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ride_status_enum = sa.Enum(
    "SEARCHING_DRIVER",
    "DRIVER_ASSIGNED",
    "DRIVER_ON_THE_WAY",
    "PICKED_UP",
    "COMPLETED",
    "CANCELED",
    "FAILED",
    name="ridestatus",
)


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_id"), "customers", ["id"], unique=False)
    op.create_index(op.f("ix_customers_phone_number"), "customers", ["phone_number"], unique=True)

    op.create_table(
        "drivers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_drivers_id"), "drivers", ["id"], unique=False)
    op.create_index(op.f("ix_drivers_phone_number"), "drivers", ["phone_number"], unique=True)

    op.create_table(
        "rides",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("driver_id", sa.Integer(), nullable=True),
        sa.Column("origin_text", sa.Text(), nullable=True),
        sa.Column("destination_text", sa.Text(), nullable=True),
        sa.Column("notes_text", sa.Text(), nullable=True),
        sa.Column("origin_city", sa.String(length=80), nullable=True),
        sa.Column("origin_street", sa.String(length=120), nullable=True),
        sa.Column("origin_house_number", sa.String(length=20), nullable=True),
        sa.Column("destination_city", sa.String(length=80), nullable=True),
        sa.Column("destination_street", sa.String(length=120), nullable=True),
        sa.Column("destination_house_number", sa.String(length=20), nullable=True),
        sa.Column("price_amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("status", ride_status_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rides_customer_id"), "rides", ["customer_id"], unique=False)
    op.create_index(op.f("ix_rides_driver_id"), "rides", ["driver_id"], unique=False)
    op.create_index(op.f("ix_rides_id"), "rides", ["id"], unique=False)
    op.create_index(op.f("ix_rides_status"), "rides", ["status"], unique=False)

    op.create_table(
        "ride_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ride_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["ride_id"], ["rides.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ride_events_id"), "ride_events", ["id"], unique=False)
    op.create_index(op.f("ix_ride_events_ride_id"), "ride_events", ["ride_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ride_events_ride_id"), table_name="ride_events")
    op.drop_index(op.f("ix_ride_events_id"), table_name="ride_events")
    op.drop_table("ride_events")
    op.drop_index(op.f("ix_rides_status"), table_name="rides")
    op.drop_index(op.f("ix_rides_id"), table_name="rides")
    op.drop_index(op.f("ix_rides_driver_id"), table_name="rides")
    op.drop_index(op.f("ix_rides_customer_id"), table_name="rides")
    op.drop_table("rides")
    op.drop_index(op.f("ix_drivers_phone_number"), table_name="drivers")
    op.drop_index(op.f("ix_drivers_id"), table_name="drivers")
    op.drop_table("drivers")
    op.drop_index(op.f("ix_customers_phone_number"), table_name="customers")
    op.drop_index(op.f("ix_customers_id"), table_name="customers")
    op.drop_table("customers")
    ride_status_enum.drop(op.get_bind(), checkfirst=False)
