from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modeles.categorie_depense import CategorieDepense
    from app.modeles.depense_recurrente import DepenseRecurrente
    from app.modeles.periode import Periode


class Depense(Base):
    __tablename__ = "depenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    periode_id: Mapped[int] = mapped_column(ForeignKey("periodes.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    fournisseur: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie_id: Mapped[int] = mapped_column(ForeignKey("categories_depense.id"), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    saisie_ttc: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    montant_saisi: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    depense_recurrente_id: Mapped[int | None] = mapped_column(
        ForeignKey("depenses_recurrentes.id", ondelete="SET NULL"), nullable=True
    )

    periode: Mapped[Periode] = relationship(back_populates="depenses")
    categorie: Mapped[CategorieDepense] = relationship(back_populates="depenses")
    depense_recurrente: Mapped[DepenseRecurrente | None] = relationship(back_populates="depenses_generees")
