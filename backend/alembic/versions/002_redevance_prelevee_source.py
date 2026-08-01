"""redevance prelevee a la source

Revision ID: 002
Revises: 001
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "configuration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("redevance_prelevee_source", sa.Boolean(), nullable=False, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("INSERT INTO configuration (id, redevance_prelevee_source) VALUES (1, false)")
    op.add_column("revenus", sa.Column("nombre_redevances", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("revenus", "nombre_redevances")
    op.drop_table("configuration")
