"""add stations table

Revision ID: 20260410_0003
Revises: 20260410_0002
Create Date: 2026-04-10 00:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260410_0003"
down_revision: Union[str, Sequence[str], None] = "20260410_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "stations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stations_id"), "stations", ["id"], unique=False)
    op.create_index(op.f("ix_stations_is_active"), "stations", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_stations_is_active"), table_name="stations")
    op.drop_index(op.f("ix_stations_id"), table_name="stations")
    op.drop_table("stations")
