"""isolation multi-utilisateurs

Ajoute utilisateur_id (FK CASCADE) sur periodes, categories_depense,
depenses_recurrentes, comptes_tresorerie et parametres_fiscaux. Chaque
utilisateur a désormais ses propres données, isolées les unes des autres.

Robuste pour un déploiement neuf (tables vides) comme pour une base
existante (backfill sur le premier utilisateur, ou un utilisateur
« placeholder » créé si des données orphelines existent sans aucun compte).

Revision ID: 006
Revises: 005
Create Date: 2026-07-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES_A_ISOLER = (
    "periodes",
    "categories_depense",
    "depenses_recurrentes",
    "comptes_tresorerie",
    "parametres_fiscaux",
)


def _premier_utilisateur_id(bind) -> int | None:
    ligne = bind.execute(sa.text("SELECT id FROM utilisateurs ORDER BY id LIMIT 1")).first()
    return ligne[0] if ligne else None


def _table_a_des_lignes(bind, table: str) -> bool:
    return bind.execute(sa.text(f"SELECT 1 FROM {table} LIMIT 1")).first() is not None


def _creer_utilisateur_placeholder(bind) -> int:
    """Utilisateur technique pour rattacher des données orphelines (base existante sans compte)."""
    ligne = bind.execute(
        sa.text(
            """
            INSERT INTO utilisateurs (email, mot_de_passe_hash, actif)
            VALUES ('migration-006-placeholder@local', '!desactive!', false)
            RETURNING id
            """
        )
    ).first()
    return ligne[0]


def upgrade() -> None:
    bind = op.get_bind()

    for table in TABLES_A_ISOLER:
        op.add_column(table, sa.Column("utilisateur_id", sa.Integer(), nullable=True))

    utilisateur_id = _premier_utilisateur_id(bind)
    if utilisateur_id is None and any(_table_a_des_lignes(bind, table) for table in TABLES_A_ISOLER):
        utilisateur_id = _creer_utilisateur_placeholder(bind)

    if utilisateur_id is not None:
        for table in TABLES_A_ISOLER:
            bind.execute(
                sa.text(f"UPDATE {table} SET utilisateur_id = :uid WHERE utilisateur_id IS NULL"),
                {"uid": utilisateur_id},
            )

    # Anciennes contraintes remplacées par des contraintes composites incluant utilisateur_id
    op.execute("ALTER TABLE periodes DROP CONSTRAINT IF EXISTS uq_periode_annee_mois")
    op.execute("ALTER TABLE categories_depense DROP CONSTRAINT IF EXISTS categories_depense_nom_key")
    op.execute("ALTER TABLE parametres_fiscaux DROP CONSTRAINT IF EXISTS parametres_fiscaux_pkey")

    for table in TABLES_A_ISOLER:
        op.alter_column(table, "utilisateur_id", nullable=False)
        op.create_foreign_key(
            f"fk_{table}_utilisateur_id",
            table,
            "utilisateurs",
            ["utilisateur_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_index(f"ix_{table}_utilisateur_id", table, ["utilisateur_id"])

    op.create_primary_key("parametres_fiscaux_pkey", "parametres_fiscaux", ["utilisateur_id", "annee"])
    op.create_unique_constraint(
        "uq_periode_utilisateur_annee_mois", "periodes", ["utilisateur_id", "annee", "mois"]
    )
    op.create_unique_constraint(
        "uq_categorie_utilisateur_nom", "categories_depense", ["utilisateur_id", "nom"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_categorie_utilisateur_nom", "categories_depense", type_="unique")
    op.drop_constraint("uq_periode_utilisateur_annee_mois", "periodes", type_="unique")
    op.drop_constraint("parametres_fiscaux_pkey", "parametres_fiscaux", type_="primary")

    for table in TABLES_A_ISOLER:
        op.drop_index(f"ix_{table}_utilisateur_id", table_name=table)
        op.drop_constraint(f"fk_{table}_utilisateur_id", table, type_="foreignkey")
        op.drop_column(table, "utilisateur_id")

    op.create_primary_key("parametres_fiscaux_pkey", "parametres_fiscaux", ["annee"])
    op.create_unique_constraint("uq_periode_annee_mois", "periodes", ["annee", "mois"])
    op.create_unique_constraint("categories_depense_nom_key", "categories_depense", ["nom"])
