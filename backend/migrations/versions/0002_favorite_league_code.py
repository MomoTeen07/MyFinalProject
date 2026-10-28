"""Store the competition for each favorite so it links back to its team.

Revision ID: 0002_favorite_league_code
Revises: 0001_initial_schema
Create Date: 2026-10-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_favorite_league_code"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if inspector.has_table("favorites") and "league_code" not in {
        column["name"] for column in inspector.get_columns("favorites")
    }:
        op.add_column("favorites", sa.Column("league_code", sa.String(length=10), nullable=True))


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if inspector.has_table("favorites") and "league_code" in {
        column["name"] for column in inspector.get_columns("favorites")
    }:
        op.drop_column("favorites", "league_code")
