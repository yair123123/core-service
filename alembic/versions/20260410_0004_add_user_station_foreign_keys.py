"""add user station foreign keys via link tables

Revision ID: 20260410_0004
Revises: 20260410_0003
Create Date: 2026-04-10 01:00:00
"""

from typing import Any, Sequence, Union
import json

from alembic import op
import sqlalchemy as sa


revision: str = "20260410_0004"
down_revision: Union[str, Sequence[str], None] = "20260410_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_dispatcher_stations = sa.table(
    "user_dispatcher_stations",
    sa.column("user_id", sa.Integer()),
    sa.column("station_id", sa.Integer()),
)

user_driver_stations = sa.table(
    "user_driver_stations",
    sa.column("user_id", sa.Integer()),
    sa.column("station_id", sa.Integer()),
)


def _normalize_ids(raw: Any) -> list[int]:
    if raw is None:
        return []
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []
    if not isinstance(raw, list):
        return []
    return [value for value in raw if isinstance(value, int)]


def upgrade() -> None:
    op.create_table(
        "user_dispatcher_stations",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "station_id"),
    )
    op.create_index(op.f("ix_user_dispatcher_stations_user_id"), "user_dispatcher_stations", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_user_dispatcher_stations_station_id"), "user_dispatcher_stations", ["station_id"], unique=False
    )

    op.create_table(
        "user_driver_stations",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("station_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "station_id"),
    )
    op.create_index(op.f("ix_user_driver_stations_user_id"), "user_driver_stations", ["user_id"], unique=False)
    op.create_index(op.f("ix_user_driver_stations_station_id"), "user_driver_stations", ["station_id"], unique=False)

    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, dispatcher_stations_id, driver_stations_id FROM users")).mappings().all()

    dispatcher_rows: list[dict[str, int]] = []
    driver_rows: list[dict[str, int]] = []
    for row in rows:
        user_id = int(row["id"])
        dispatcher_ids = _normalize_ids(row["dispatcher_stations_id"])
        driver_ids = _normalize_ids(row["driver_stations_id"])

        for station_id in dispatcher_ids:
            dispatcher_rows.append({"user_id": user_id, "station_id": station_id})

        for station_id in driver_ids:
            driver_rows.append({"user_id": user_id, "station_id": station_id})

    if dispatcher_rows:
        op.bulk_insert(user_dispatcher_stations, dispatcher_rows)
    if driver_rows:
        op.bulk_insert(user_driver_stations, driver_rows)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_driver_stations_station_id"), table_name="user_driver_stations")
    op.drop_index(op.f("ix_user_driver_stations_user_id"), table_name="user_driver_stations")
    op.drop_table("user_driver_stations")

    op.drop_index(op.f("ix_user_dispatcher_stations_station_id"), table_name="user_dispatcher_stations")
    op.drop_index(op.f("ix_user_dispatcher_stations_user_id"), table_name="user_dispatcher_stations")
    op.drop_table("user_dispatcher_stations")
