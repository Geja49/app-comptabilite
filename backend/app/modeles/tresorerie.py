from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TypeCompteTresorerie(StrEnum):
    CAISSE = "caisse"
    BANQUE = "banque"


class TypeOperationTresorerie(StrEnum):
    ENCAISSEMENT = "encaissement"
    DEPOT = "depot"
    RETRAIT = "retrait"
    PAIEMENT = "paiement"
    TRANSFERT = "transfert"
    AJUSTEMENT = "ajustement"


class CompteTresorerie(Base):
    __tablename__ = "comptes_tresorerie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    type_compte: Mapped[str] = mapped_column(String(20), nullable=False)
    solde_ouverture: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    operations: Mapped[list["OperationTresorerie"]] = relationship(
        back_populates="compte",
        foreign_keys="OperationTresorerie.compte_id",
    )


class OperationTresorerie(Base):
    __tablename__ = "operations_tresorerie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_operation: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    type_operation: Mapped[str] = mapped_column(String(30), nullable=False)
    compte_id: Mapped[int] = mapped_column(ForeignKey("comptes_tresorerie.id"), nullable=False)
    compte_contrepartie_id: Mapped[int | None] = mapped_column(
        ForeignKey("comptes_tresorerie.id"),
        nullable=True,
    )
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    est_entree: Mapped[bool] = mapped_column(Boolean, nullable=False)
    libelle: Mapped[str] = mapped_column(String(255), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    revenu_id: Mapped[int | None] = mapped_column(ForeignKey("revenus.id"), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    compte: Mapped[CompteTresorerie] = relationship(
        back_populates="operations",
        foreign_keys=[compte_id],
    )
    compte_contrepartie: Mapped[CompteTresorerie | None] = relationship(
        foreign_keys=[compte_contrepartie_id],
    )
