from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modeles.categorie_depense import CategorieDepense
    from app.modeles.depense import Depense


class FrequenceDepenseRecurrente(StrEnum):
    MENSUELLE = "mensuelle"
    PAR_JOUR_TRAVAIL = "par_jour_travail"


class DepenseRecurrente(Base):
    __tablename__ = "depenses_recurrentes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fournisseur: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie_id: Mapped[int] = mapped_column(ForeignKey("categories_depense.id"), nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    montant_ttc: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    jour_du_mois: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    frequence: Mapped[str] = mapped_column(
        String(30), nullable=False, default=FrequenceDepenseRecurrente.MENSUELLE.value
    )
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    categorie: Mapped[CategorieDepense] = relationship(back_populates="depenses_recurrentes")
    depenses_generees: Mapped[list[Depense]] = relationship(back_populates="depense_recurrente")
