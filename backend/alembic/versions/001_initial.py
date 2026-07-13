"""migration initiale

Revision ID: 001
Revises:
Create Date: 2026-07-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories_depense",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("est_systeme", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nom"),
    )
    op.create_table(
        "periodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("annee", sa.Integer(), nullable=False),
        sa.Column("mois", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("annee", "mois", name="uq_periode_annee_mois"),
    )
    op.create_table(
        "depenses_recurrentes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fournisseur", sa.String(length=200), nullable=False),
        sa.Column("categorie_id", sa.Integer(), nullable=False),
        sa.Column("montant", sa.Numeric(12, 2), nullable=False),
        sa.Column("montant_ttc", sa.Boolean(), nullable=False),
        sa.Column("jour_du_mois", sa.Integer(), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["categorie_id"], ["categories_depense.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "depenses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("periode_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("fournisseur", sa.String(length=200), nullable=False),
        sa.Column("categorie_id", sa.Integer(), nullable=False),
        sa.Column("montant_ht", sa.Numeric(12, 2), nullable=False),
        sa.Column("saisie_ttc", sa.Boolean(), nullable=False),
        sa.Column("montant_saisi", sa.Numeric(12, 2), nullable=False),
        sa.Column("depense_recurrente_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["categorie_id"], ["categories_depense.id"]),
        sa.ForeignKeyConstraint(["depense_recurrente_id"], ["depenses_recurrentes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["periode_id"], ["periodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "entrees_kilometrage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("periode_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("odometre_debut", sa.Numeric(12, 1), nullable=False),
        sa.Column("odometre_fin", sa.Numeric(12, 1), nullable=False),
        sa.Column("km_professionnels", sa.Numeric(12, 1), nullable=False),
        sa.ForeignKeyConstraint(["periode_id"], ["periodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("periode_id", "date", name="uq_km_periode_date"),
    )
    op.create_table(
        "revenus",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("periode_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("nombre_courses", sa.Integer(), nullable=False),
        sa.Column("revenu_brut", sa.Numeric(12, 2), nullable=False),
        sa.Column("pourboires", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["periode_id"], ["periodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("periode_id", "date", name="uq_revenu_periode_date"),
    )


def downgrade() -> None:
    op.drop_table("revenus")
    op.drop_table("entrees_kilometrage")
    op.drop_table("depenses")
    op.drop_table("depenses_recurrentes")
    op.drop_table("periodes")
    op.drop_table("categories_depense")
