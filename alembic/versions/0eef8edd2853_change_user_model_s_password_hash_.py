"""change User model's password_hash column character limits

Revision ID: 0eef8edd2853
Revises: 379aa4eb01b1
Create Date: 2026-08-22 14:06:47.768166

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0eef8edd2853"
down_revision: str | Sequence[str] | None = "379aa4eb01b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=50),
        existing_nullable=False,
    )
