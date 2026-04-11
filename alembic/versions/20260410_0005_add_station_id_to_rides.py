"""add station id to rides

Revision ID: 20260410_0005
Revises: 20260410_0004
Create Date: 2026-04-10 02:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260410_0005"
down_revision: Union[str, Sequence[str], None] = "20260410_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rides", sa.Column("station_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_rides_station_id"), "rides", ["station_id"], unique=False)
    op.create_foreign_key("fk_rides_station_id_stations", "rides", "stations", ["station_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_rides_station_id_stations", "rides", type_="foreignkey")
    op.drop_index(op.f("ix_rides_station_id"), table_name="rides")
    op.drop_column("rides", "station_id")
