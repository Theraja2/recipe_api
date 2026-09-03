"""add public recipes

Revision ID: 3a949bce87c8
Revises: 1c806a910aba
Create Date: 2026-09-03 23:36:16.131637

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3a949bce87c8"
down_revision: Union[str, Sequence[str], None] = "1c806a910aba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "recipes",
        sa.Column(
            "is_public",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "recipes",
        sa.Column(
            "prep_minutes",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "recipes",
        sa.Column(
            "cook_minutes",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("recipes", "cook_minutes")
    op.drop_column("recipes", "prep_minutes")
    op.drop_column("recipes", "is_public")