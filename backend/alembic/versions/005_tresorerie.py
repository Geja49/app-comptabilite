"""tresorerie caisse et banque

Revision ID: 005
Revises: 004
Create Date: 2026-07-17
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comptes_tresorerie",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("type_compte", sa.String(length=20), nullable=False),
        sa.Column("solde_ouverture", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("cree_le", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_table(
        "operations_tresorerie",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date_operation", sa.Date(), nullable=False),
        sa.Column("type_operation", sa.String(length=30), nullable=False),
        sa.Column("compte_id", sa.Integer(), sa.ForeignKey("comptes_tresorerie.id"), nullable=False),
        sa.Column(
            "compte_contrepartie_id",
            sa.Integer(),
            sa.ForeignKey("comptes_tresorerie.id"),
            nullable=True,
        ),
        sa.Column("montant", sa.Numeric(12, 2), nullable=False),
        sa.Column("est_entree", sa.Boolean(), nullable=False),
        sa.Column("libelle", sa.String(length=255), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("revenu_id", sa.Integer(), sa.ForeignKey("revenus.id"), nullable=True),
        sa.Column("cree_le", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_operations_tresorerie_date", "operations_tresorerie", ["date_operation"])


def downgrade() -> None:
    op.drop_index("ix_operations_tresorerie_date", table_name="operations_tresorerie")
    op.drop_table("operations_tresorerie")
    op.drop_table("comptes_tresorerie")
