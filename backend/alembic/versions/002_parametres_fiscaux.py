"""parametres fiscaux

Revision ID: 002
Revises: 001
Create Date: 2026-07-13
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
        "parametres_fiscaux",
        sa.Column("annee", sa.Integer(), nullable=False),
        sa.Column("methode_tps_tvq", sa.String(length=20), nullable=False),
        sa.Column("tps_taux_reguliere", sa.Numeric(8, 5), nullable=False),
        sa.Column("tvq_taux_reguliere", sa.Numeric(8, 5), nullable=False),
        sa.Column("tps_taux_rapide", sa.Numeric(8, 5), nullable=False),
        sa.Column("tvq_taux_rapide", sa.Numeric(8, 5), nullable=False),
        sa.Column("rabais_rapide_taux", sa.Numeric(8, 5), nullable=False),
        sa.Column("rabais_rapide_plafond", sa.Numeric(12, 2), nullable=False),
        sa.Column("redevance_par_course", sa.Numeric(8, 2), nullable=False),
        sa.PrimaryKeyConstraint("annee"),
    )
    op.execute(
        """
        INSERT INTO parametres_fiscaux (
            annee, methode_tps_tvq,
            tps_taux_reguliere, tvq_taux_reguliere,
            tps_taux_rapide, tvq_taux_rapide,
            rabais_rapide_taux, rabais_rapide_plafond,
            redevance_par_course
        ) VALUES (
            2026, 'reguliere',
            0.05, 0.09975,
            0.036, 0.066,
            0.01, 30000,
            0.90
        )
        """
    )


def downgrade() -> None:
    op.drop_table("parametres_fiscaux")
