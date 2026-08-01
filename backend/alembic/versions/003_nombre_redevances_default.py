"""nombre_redevances default 0

Revision ID: 003
Revises: 002
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE revenus SET nombre_redevances = 0 WHERE nombre_redevances IS NULL")
    op.alter_column("revenus", "nombre_redevances", nullable=False, server_default="0")


def downgrade() -> None:
    op.alter_column("revenus", "nombre_redevances", nullable=True, server_default=None)
