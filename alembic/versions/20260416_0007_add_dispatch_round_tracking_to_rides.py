"""add dispatch round tracking to rides

Revision ID: 20260416_0007
Revises: 20260412_0006
Create Date: 2026-04-16 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260416_0007"
down_revision: Union[str, Sequence[str], None] = "20260412_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rides", sa.Column("dispatch_round_number", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("rides", sa.Column("dispatch_current_round_id", sa.String(length=120), nullable=True))
    op.add_column("rides", sa.Column("last_dispatch_result_round_id", sa.String(length=120), nullable=True))
    op.add_column("rides", sa.Column("last_dispatch_result_status", sa.String(length=40), nullable=True))
    op.alter_column("rides", "dispatch_round_number", server_default=None)


def downgrade() -> None:
    op.drop_column("rides", "last_dispatch_result_status")
    op.drop_column("rides", "last_dispatch_result_round_id")
    op.drop_column("rides", "dispatch_current_round_id")
    op.drop_column("rides", "dispatch_round_number")
