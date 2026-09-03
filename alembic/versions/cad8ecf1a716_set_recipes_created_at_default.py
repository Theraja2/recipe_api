"""set recipes created_at default

Revision ID: cad8ecf1a716
Revises: b50ac40ffa9d
Create Date: 2026-09-03 11:41:45.551147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cad8ecf1a716'
down_revision: Union[str, Sequence[str], None] = 'b50ac40ffa9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "recipes",
        "created_at",
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )



def downgrade() -> None:
    op.alter_column(
        "recipes",
        "created_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=False,
    )