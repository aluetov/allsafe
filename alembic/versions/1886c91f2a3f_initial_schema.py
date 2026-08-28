"""initial schema

Revision ID: 1886c91f2a3f
Revises:
Create Date: 2026-08-19 03:14:50.829070

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1886c91f2a3f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "domains",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("qname", sa.String(), nullable=False),
        sa.Column("canonical_name", sa.String(), nullable=False),
        sa.Column("record_type", sa.String(), nullable=False),
        sa.Column("record_class", sa.String(), nullable=False),
        sa.Column("expiration", sa.Float(), nullable=False),
        sa.Column("records", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_domains")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("domains")
