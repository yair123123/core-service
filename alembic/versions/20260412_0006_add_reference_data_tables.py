"""add reference data tables

Revision ID: 20260412_0006
Revises: 20260410_0005
Create Date: 2026-04-12 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260412_0006"
down_revision: Union[str, Sequence[str], None] = "20260410_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


cities_table = sa.table(
    "cities",
    sa.column("name", sa.String(length=120)),
    sa.column("is_active", sa.Boolean()),
)

price_templates_table = sa.table(
    "price_templates",
    sa.column("name", sa.String(length=120)),
    sa.column("value", sa.Numeric(10, 2)),
    sa.column("is_active", sa.Boolean()),
)

additional_message_templates_table = sa.table(
    "additional_message_templates",
    sa.column("text", sa.Text()),
    sa.column("is_active", sa.Boolean()),
)


def upgrade() -> None:
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cities_id"), "cities", ["id"], unique=False)
    op.create_index(op.f("ix_cities_is_active"), "cities", ["is_active"], unique=False)

    op.create_table(
        "price_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("value", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_templates_id"), "price_templates", ["id"], unique=False)
    op.create_index(op.f("ix_price_templates_is_active"), "price_templates", ["is_active"], unique=False)

    op.create_table(
        "additional_message_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_additional_message_templates_id"),
        "additional_message_templates",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_additional_message_templates_is_active"),
        "additional_message_templates",
        ["is_active"],
        unique=False,
    )

    op.bulk_insert(
        cities_table,
        [
            {"name": "Jerusalem", "is_active": True},
            {"name": "Tel Aviv", "is_active": True},
            {"name": "Haifa", "is_active": True},
        ],
    )
    op.bulk_insert(
        price_templates_table,
        [
            {"name": "Regular", "value": 50, "is_active": True},
            {"name": "Airport", "value": 120, "is_active": True},
            {"name": "Night", "value": 80, "is_active": True},
        ],
    )
    op.bulk_insert(
        additional_message_templates_table,
        [
            {"text": "Call before arrival", "is_active": True},
            {"text": "Large luggage", "is_active": True},
            {"text": "Passenger with stroller", "is_active": True},
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_additional_message_templates_is_active"), table_name="additional_message_templates")
    op.drop_index(op.f("ix_additional_message_templates_id"), table_name="additional_message_templates")
    op.drop_table("additional_message_templates")

    op.drop_index(op.f("ix_price_templates_is_active"), table_name="price_templates")
    op.drop_index(op.f("ix_price_templates_id"), table_name="price_templates")
    op.drop_table("price_templates")

    op.drop_index(op.f("ix_cities_is_active"), table_name="cities")
    op.drop_index(op.f("ix_cities_id"), table_name="cities")
    op.drop_table("cities")
