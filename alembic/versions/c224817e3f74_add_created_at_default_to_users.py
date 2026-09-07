"""add created_at default to users

Revision ID: c224817e3f74
Revises: 3a949bce87c8
Create Date: 2026-09-05 10:23:04.624710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c224817e3f74'
down_revision: Union[str, Sequence[str], None] = '3a949bce87c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )




def downgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )
