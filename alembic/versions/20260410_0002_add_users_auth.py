"""add users for authentication

Revision ID: 20260410_0002
Revises: 20260325_0001
Create Date: 2026-04-10 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260410_0002"
down_revision: Union[str, Sequence[str], None] = "20260325_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("can_receive_rides_for_non_payment", sa.Boolean(), nullable=False),
        sa.Column("is_dispatcher", sa.Boolean(), nullable=False),
        sa.Column("dispatcher_stations_id", sa.JSON(), nullable=False),
        sa.Column("driver_stations_id", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
