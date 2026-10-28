"""Adopt or create the initial application schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # The first app version created these tables with SQLAlchemy at startup.
    # Adopt them in place so existing users and favorites are retained.
    if not inspector.has_table("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    inspector = inspect(bind)
    user_indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_email" not in user_indexes:
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if not inspector.has_table("favorites"):
        op.create_table(
            "favorites",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("team_id", sa.Integer(), nullable=False),
            sa.Column("team_name", sa.String(length=150), nullable=False),
            sa.Column("team_crest", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.UniqueConstraint("user_id", "team_id", name="uq_user_team_favorite"),
        )
        return

    unique_constraints = inspect(bind).get_unique_constraints("favorites")
    has_user_team_unique = any(
        set(constraint.get("column_names") or []) == {"user_id", "team_id"}
        for constraint in unique_constraints
    )
    if not has_user_team_unique:
        op.create_unique_constraint(
            "uq_user_team_favorite", "favorites", ["user_id", "team_id"]
        )


def downgrade() -> None:
    # This baseline may have adopted a database with user data. Keep the schema
    # in place if a developer moves Alembic back to base.
    pass
