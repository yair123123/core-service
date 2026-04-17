"""add addresses table and ride address foreign keys

Revision ID: 20260417_0008
Revises: 20260416_0007
Create Date: 2026-04-17 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260417_0008"
down_revision: Union[str, Sequence[str], None] = "20260416_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("street", sa.String(length=120), nullable=False),
        sa.Column("house_number", sa.String(length=20), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("formatted_address", sa.Text(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=True),
        sa.Column("provider_place_id", sa.String(length=255), nullable=True),
        sa.Column("match_quality", sa.String(length=20), nullable=True),
        sa.Column("partial_match", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("raw_query_json", sa.JSON(), nullable=True),
        sa.Column("warnings_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_addresses_id"), "addresses", ["id"], unique=False)

    op.add_column("rides", sa.Column("origin_address_id", sa.Integer(), nullable=True))
    op.add_column("rides", sa.Column("destination_address_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_rides_origin_address_id"), "rides", ["origin_address_id"], unique=False)
    op.create_index(op.f("ix_rides_destination_address_id"), "rides", ["destination_address_id"], unique=False)
    op.create_foreign_key("fk_rides_origin_address", "rides", "addresses", ["origin_address_id"], ["id"])
    op.create_foreign_key(
        "fk_rides_destination_address", "rides", "addresses", ["destination_address_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_rides_destination_address", "rides", type_="foreignkey")
    op.drop_constraint("fk_rides_origin_address", "rides", type_="foreignkey")
    op.drop_index(op.f("ix_rides_destination_address_id"), table_name="rides")
    op.drop_index(op.f("ix_rides_origin_address_id"), table_name="rides")
    op.drop_column("rides", "destination_address_id")
    op.drop_column("rides", "origin_address_id")

    op.drop_index(op.f("ix_addresses_id"), table_name="addresses")
    op.drop_table("addresses")
