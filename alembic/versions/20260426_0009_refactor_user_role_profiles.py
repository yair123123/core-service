"""refactor user role profiles

Revision ID: 20260426_0009
Revises: 20260417_0008
Create Date: 2026-04-26 00:00:00
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260426_0009"
down_revision: Union[str, Sequence[str], None] = "20260417_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEGACY_USER_ROLE_COLUMNS = (
    "gender",
    "rating",
    "can_receive_rides_for_non_payment",
    "is_dispatcher",
    "dispatcher_stations_id",
    "driver_stations_id",
)


def _table_exists(inspector: sa.Inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _column_exists(inspector: sa.Inspector, table_name: str, column_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _index_exists(inspector: sa.Inspector, table_name: str, index_name: str) -> bool:
    if not _table_exists(inspector, table_name):
        return False
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _fetch_rows(bind: sa.Connection, query: str) -> list[dict[str, Any]]:
    return [dict(row) for row in bind.execute(sa.text(query)).mappings().all()]


def _get_table_column_map(inspector: sa.Inspector, table_name: str) -> dict[str, dict[str, Any]]:
    if not _table_exists(inspector, table_name):
        return {}
    return {column["name"]: column for column in inspector.get_columns(table_name)}


def _relax_legacy_user_columns(bind: sa.Connection, inspector: sa.Inspector) -> dict[str, dict[str, Any]]:
    user_columns = _get_table_column_map(inspector, "users")
    for column_name in LEGACY_USER_ROLE_COLUMNS:
        column = user_columns.get(column_name)
        if column is None or column.get("nullable", True):
            continue

        existing_type = column["type"]
        op.alter_column("users", column_name, existing_type=existing_type, nullable=True)

    return _get_table_column_map(sa.inspect(bind), "users")


def _get_or_create_user(
    bind: sa.Connection,
    *,
    user_columns: dict[str, dict[str, Any]],
    username: str,
    phone_number: str | None,
    password_hash: str,
    is_active: bool,
) -> int:
    has_phone_number = "phone_number" in user_columns
    has_rules = "rules" in user_columns

    if phone_number and has_phone_number:
        existing_id = bind.execute(
            sa.text("SELECT id FROM users WHERE phone_number = :phone_number"),
            {"phone_number": phone_number},
        ).scalar_one_or_none()
        if existing_id is not None:
            assignments = ["username = COALESCE(username, :username)"]
            params: dict[str, Any] = {
                "user_id": existing_id,
                "username": username,
                "password_hash": password_hash,
                "is_active": is_active,
            }
            if "password_hash" in user_columns:
                assignments.append("password_hash = COALESCE(password_hash, :password_hash)")
            if "is_active" in user_columns:
                assignments.append("is_active = COALESCE(is_active, :is_active)")
            if has_phone_number:
                assignments.append("phone_number = COALESCE(phone_number, :phone_number)")
                params["phone_number"] = phone_number

            bind.execute(
                sa.text(
                    f"""
                    UPDATE users
                    SET {", ".join(assignments)}
                    WHERE id = :user_id
                    """
                ),
                params,
            )
            return int(existing_id)

    existing_id = bind.execute(
        sa.text("SELECT id FROM users WHERE username = :username"),
        {"username": username},
    ).scalar_one_or_none()
    if existing_id is not None:
        if has_phone_number:
            bind.execute(
                sa.text(
                    """
                    UPDATE users
                    SET phone_number = COALESCE(phone_number, :phone_number)
                    WHERE id = :user_id
                    """
                ),
                {"user_id": existing_id, "phone_number": phone_number},
            )
        return int(existing_id)

    insert_values: dict[str, Any] = {
        "username": username,
        "password_hash": password_hash,
        "is_active": is_active,
    }
    if has_phone_number:
        insert_values["phone_number"] = phone_number
    if has_rules:
        insert_values["rules"] = False

    columns_sql = ", ".join(insert_values.keys())
    params_sql = ", ".join(f":{column_name}" for column_name in insert_values)
    return int(
        bind.execute(
            sa.text(
                f"""
                INSERT INTO users ({columns_sql})
                VALUES ({params_sql})
                RETURNING id
                """
            ),
            insert_values,
        ).scalar_one()
    )


def _get_or_create_profile(
    bind: sa.Connection,
    *,
    table_name: str,
    user_id: int,
    values: dict[str, Any],
) -> int:
    existing_id = bind.execute(
        sa.text(f"SELECT id FROM {table_name} WHERE user_id = :user_id"),
        {"user_id": user_id},
    ).scalar_one_or_none()
    if existing_id is not None:
        assignments = ", ".join(f"{column} = :{column}" for column in values)
        bind.execute(
            sa.text(f"UPDATE {table_name} SET {assignments} WHERE id = :profile_id"),
            {"profile_id": existing_id, **values},
        )
        return int(existing_id)

    columns = ", ".join(["user_id", *values.keys()])
    placeholders = ", ".join([":user_id", *[f":{column}" for column in values]])
    return int(
        bind.execute(
            sa.text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id"),
            {"user_id": user_id, **values},
        ).scalar_one()
    )


def _insert_missing_links(
    bind: sa.Connection,
    *,
    table_name: str,
    fk_column: str,
    rows: Iterable[dict[str, int]],
) -> None:
    for row in rows:
        existing = bind.execute(
            sa.text(
                f"SELECT 1 FROM {table_name} WHERE {fk_column} = :profile_id AND station_id = :station_id"
            ),
            {"profile_id": row[fk_column], "station_id": row["station_id"]},
        ).scalar_one_or_none()
        if existing is None:
            bind.execute(
                sa.text(f"INSERT INTO {table_name} ({fk_column}, station_id) VALUES (:profile_id, :station_id)"),
                {"profile_id": row[fk_column], "station_id": row["station_id"]},
            )


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    with op.batch_alter_table("users") as batch_op:
        if not _column_exists(inspector, "users", "rules"):
            batch_op.add_column(sa.Column("rules", sa.Boolean(), nullable=False, server_default=sa.false()))
        if not _column_exists(inspector, "users", "phone_number"):
            batch_op.add_column(sa.Column("phone_number", sa.String(length=20), nullable=True))
    inspector = sa.inspect(bind)
    if not _index_exists(inspector, "users", "ix_users_phone_number"):
        op.create_index("ix_users_phone_number", "users", ["phone_number"], unique=True)
    if _column_exists(inspector, "users", "rules"):
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column("rules", server_default=None)

    inspector = sa.inspect(bind)
    user_columns = _relax_legacy_user_columns(bind, inspector)

    if not _table_exists(inspector, "driver_profiles"):
        op.create_table(
            "driver_profiles",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("display_name", sa.String(length=120), nullable=True),
            sa.Column("gender", sa.String(length=20), nullable=True),
            sa.Column("rating", sa.Float(), nullable=True),
            sa.Column("can_receive_rides_for_non_payment", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index("ix_driver_profiles_id", "driver_profiles", ["id"], unique=False)
        op.create_index("ix_driver_profiles_user_id", "driver_profiles", ["user_id"], unique=True)

    if not _table_exists(inspector, "dispatcher_profiles"):
        op.create_table(
            "dispatcher_profiles",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("display_name", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index("ix_dispatcher_profiles_id", "dispatcher_profiles", ["id"], unique=False)
        op.create_index("ix_dispatcher_profiles_user_id", "dispatcher_profiles", ["user_id"], unique=True)

    if not _table_exists(inspector, "station_owner_profiles"):
        op.create_table(
            "station_owner_profiles",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("display_name", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index("ix_station_owner_profiles_id", "station_owner_profiles", ["id"], unique=False)
        op.create_index("ix_station_owner_profiles_user_id", "station_owner_profiles", ["user_id"], unique=True)

    if not _table_exists(inspector, "driver_profile_stations"):
        op.create_table(
            "driver_profile_stations",
            sa.Column("driver_profile_id", sa.Integer(), nullable=False),
            sa.Column("station_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["driver_profile_id"], ["driver_profiles.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("driver_profile_id", "station_id"),
        )
        op.create_index("ix_driver_profile_stations_driver_profile_id", "driver_profile_stations", ["driver_profile_id"])
        op.create_index("ix_driver_profile_stations_station_id", "driver_profile_stations", ["station_id"])

    if not _table_exists(inspector, "dispatcher_profile_stations"):
        op.create_table(
            "dispatcher_profile_stations",
            sa.Column("dispatcher_profile_id", sa.Integer(), nullable=False),
            sa.Column("station_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["dispatcher_profile_id"], ["dispatcher_profiles.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("dispatcher_profile_id", "station_id"),
        )
        op.create_index(
            "ix_dispatcher_profile_stations_dispatcher_profile_id",
            "dispatcher_profile_stations",
            ["dispatcher_profile_id"],
        )
        op.create_index("ix_dispatcher_profile_stations_station_id", "dispatcher_profile_stations", ["station_id"])

    if not _table_exists(inspector, "station_owner_profile_stations"):
        op.create_table(
            "station_owner_profile_stations",
            sa.Column("station_owner_profile_id", sa.Integer(), nullable=False),
            sa.Column("station_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["station_owner_profile_id"], ["station_owner_profiles.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["station_id"], ["stations.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("station_owner_profile_id", "station_id"),
        )
        op.create_index(
            "ix_station_owner_profile_stations_station_owner_profile_id",
            "station_owner_profile_stations",
            ["station_owner_profile_id"],
        )
        op.create_index("ix_station_owner_profile_stations_station_id", "station_owner_profile_stations", ["station_id"])

    inspector = sa.inspect(bind)
    user_rows = _fetch_rows(bind, "SELECT * FROM users")
    legacy_driver_rows = _fetch_rows(bind, "SELECT * FROM drivers") if _table_exists(inspector, "drivers") else []
    legacy_driver_profile_rows = (
        _fetch_rows(bind, "SELECT * FROM driver_profile") if _table_exists(inspector, "driver_profile") else []
    )
    legacy_dispatcher_rows = (
        _fetch_rows(bind, "SELECT * FROM user_dispatcher_stations") if _table_exists(inspector, "user_dispatcher_stations") else []
    )
    legacy_driver_station_rows = (
        _fetch_rows(bind, "SELECT * FROM user_driver_stations") if _table_exists(inspector, "user_driver_stations") else []
    )

    user_driver_profile_ids: dict[int, int] = {}
    legacy_driver_id_to_profile_id: dict[int, int] = {}

    driver_station_user_ids = {int(row["user_id"]) for row in legacy_driver_station_rows}
    dispatcher_user_ids = {int(row["user_id"]) for row in legacy_dispatcher_rows}

    for row in user_rows:
        user_id = int(row["id"])
        is_driver_candidate = (
            user_id in driver_station_user_ids
            or row.get("gender") is not None
            or row.get("rating") is not None
            or bool(row.get("can_receive_rides_for_non_payment", False))
        )
        if is_driver_candidate:
            profile_id = _get_or_create_profile(
                bind,
                table_name="driver_profiles",
                user_id=user_id,
                values={
                    "display_name": row.get("username"),
                    "gender": row.get("gender"),
                    "rating": row.get("rating"),
                    "can_receive_rides_for_non_payment": bool(row.get("can_receive_rides_for_non_payment", False)),
                },
            )
            user_driver_profile_ids[user_id] = profile_id

        if bool(row.get("is_dispatcher", False)) or user_id in dispatcher_user_ids:
            _get_or_create_profile(
                bind,
                table_name="dispatcher_profiles",
                user_id=user_id,
                values={"display_name": row.get("username")},
            )

    for row in legacy_driver_rows:
        phone_number = row.get("phone_number")
        user_id = _get_or_create_user(
            bind,
            user_columns=user_columns,
            username=f"legacy_driver_{row['id']}",
            phone_number=phone_number,
            password_hash="!migrated-legacy-driver!",
            is_active=bool(row.get("is_active", True)),
        )
        profile_id = _get_or_create_profile(
            bind,
            table_name="driver_profiles",
            user_id=user_id,
            values={
                "display_name": row.get("name"),
                "gender": None,
                "rating": None,
                "can_receive_rides_for_non_payment": False,
            },
        )
        user_driver_profile_ids[user_id] = profile_id
        legacy_driver_id_to_profile_id[int(row["id"])] = profile_id

    for row in legacy_driver_profile_rows:
        existing_user_id = row.get("user_id")
        user_id = (
            int(existing_user_id)
            if existing_user_id is not None
            else _get_or_create_user(
                bind,
                user_columns=user_columns,
                username=f"legacy_driver_profile_{row['id']}",
                phone_number=row.get("phone_number"),
                password_hash="!migrated-driver-profile!",
                is_active=True,
            )
        )
        if row.get("phone_number"):
            bind.execute(
                sa.text("UPDATE users SET phone_number = COALESCE(phone_number, :phone_number) WHERE id = :user_id"),
                {"user_id": user_id, "phone_number": row.get("phone_number")},
            )
        profile_id = _get_or_create_profile(
            bind,
            table_name="driver_profiles",
            user_id=user_id,
            values={
                "display_name": row.get("display_name"),
                "gender": row.get("gender"),
                "rating": row.get("rating"),
                "can_receive_rides_for_non_payment": bool(row.get("can_receive_rides_for_non_payment", False)),
            },
        )
        user_driver_profile_ids[user_id] = profile_id
        legacy_driver_id_to_profile_id[int(row["id"])] = profile_id

    dispatcher_station_rows: list[dict[str, int]] = []
    for row in legacy_dispatcher_rows:
        user_id = int(row["user_id"])
        dispatcher_profile_id = bind.execute(
            sa.text("SELECT id FROM dispatcher_profiles WHERE user_id = :user_id"),
            {"user_id": user_id},
        ).scalar_one_or_none()
        if dispatcher_profile_id is not None:
            dispatcher_station_rows.append(
                {
                    "dispatcher_profile_id": int(dispatcher_profile_id),
                    "station_id": int(row["station_id"]),
                }
            )
    _insert_missing_links(
        bind,
        table_name="dispatcher_profile_stations",
        fk_column="dispatcher_profile_id",
        rows=dispatcher_station_rows,
    )

    driver_station_rows: list[dict[str, int]] = []
    for row in legacy_driver_station_rows:
        user_id = int(row["user_id"])
        driver_profile_id = user_driver_profile_ids.get(user_id)
        if driver_profile_id is not None:
            driver_station_rows.append(
                {
                    "driver_profile_id": driver_profile_id,
                    "station_id": int(row["station_id"]),
                }
            )
    _insert_missing_links(
        bind,
        table_name="driver_profile_stations",
        fk_column="driver_profile_id",
        rows=driver_station_rows,
    )

    ride_driver_ref_table = "users"
    for foreign_key in inspector.get_foreign_keys("rides"):
        if foreign_key.get("constrained_columns") == ["driver_id"]:
            ride_driver_ref_table = foreign_key.get("referred_table") or ride_driver_ref_table
            break

    for row in _fetch_rows(bind, "SELECT id, driver_id FROM rides WHERE driver_id IS NOT NULL"):
        old_driver_id = int(row["driver_id"])
        if ride_driver_ref_table == "drivers":
            new_driver_id = legacy_driver_id_to_profile_id.get(old_driver_id)
        elif ride_driver_ref_table == "driver_profile":
            new_driver_id = legacy_driver_id_to_profile_id.get(old_driver_id)
        else:
            new_driver_id = user_driver_profile_ids.get(old_driver_id) or legacy_driver_id_to_profile_id.get(old_driver_id)

        bind.execute(
            sa.text("UPDATE rides SET driver_id = :driver_id WHERE id = :ride_id"),
            {"ride_id": int(row["id"]), "driver_id": new_driver_id},
        )

    inspector = sa.inspect(bind)
    for foreign_key in inspector.get_foreign_keys("rides"):
        if foreign_key.get("constrained_columns") == ["driver_id"]:
            op.drop_constraint(foreign_key["name"], "rides", type_="foreignkey")

    op.create_foreign_key("fk_rides_driver_id_driver_profiles", "rides", "driver_profiles", ["driver_id"], ["id"])

    with op.batch_alter_table("users") as batch_op:
        for column_name in LEGACY_USER_ROLE_COLUMNS:
            if _column_exists(sa.inspect(bind), "users", column_name):
                batch_op.drop_column(column_name)

    if _table_exists(sa.inspect(bind), "user_driver_stations"):
        op.drop_index("ix_user_driver_stations_station_id", table_name="user_driver_stations")
        op.drop_index("ix_user_driver_stations_user_id", table_name="user_driver_stations")
        op.drop_table("user_driver_stations")

    if _table_exists(sa.inspect(bind), "user_dispatcher_stations"):
        op.drop_index("ix_user_dispatcher_stations_station_id", table_name="user_dispatcher_stations")
        op.drop_index("ix_user_dispatcher_stations_user_id", table_name="user_dispatcher_stations")
        op.drop_table("user_dispatcher_stations")

    if _table_exists(sa.inspect(bind), "driver_profile"):
        op.drop_table("driver_profile")

    if _table_exists(sa.inspect(bind), "drivers"):
        op.drop_table("drivers")


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade is not supported for the role profile refactor because legacy role columns/tables are data-migrated."
    )
