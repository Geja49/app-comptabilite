"""frequence depenses recurrentes

Revision ID: 003
Revises: 002
Create Date: 2026-07-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("depenses_recurrentes") as batch:
        batch.add_column(
            sa.Column(
                "frequence",
                sa.String(length=30),
                nullable=False,
                server_default="mensuelle",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("depenses_recurrentes") as batch:
        batch.drop_column("frequence")
