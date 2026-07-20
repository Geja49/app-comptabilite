from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modeles.depense import Depense
    from app.modeles.depense_recurrente import DepenseRecurrente


class CategorieDepense(Base):
    __tablename__ = "categories_depense"
    __table_args__ = (UniqueConstraint("utilisateur_id", "nom", name="uq_categorie_utilisateur_nom"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    est_systeme: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    depenses: Mapped[list[Depense]] = relationship(back_populates="categorie")
    depenses_recurrentes: Mapped[list[DepenseRecurrente]] = relationship(back_populates="categorie")
