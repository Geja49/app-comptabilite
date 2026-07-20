from decimal import Decimal
from enum import StrEnum

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MethodeTpsTvq(StrEnum):
    REGULIERE = "reguliere"
    RAPIDE = "rapide"


class ParametresFiscaux(Base):
    __tablename__ = "parametres_fiscaux"

    utilisateur_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    annee: Mapped[int] = mapped_column(Integer, primary_key=True)
    methode_tps_tvq: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MethodeTpsTvq.REGULIERE.value
    )
    tps_taux_reguliere: Mapped[Decimal] = mapped_column(Numeric(8, 5), nullable=False, default=Decimal("0.05"))
    tvq_taux_reguliere: Mapped[Decimal] = mapped_column(Numeric(8, 5), nullable=False, default=Decimal("0.09975"))
    tps_taux_rapide: Mapped[Decimal] = mapped_column(Numeric(8, 5), nullable=False, default=Decimal("0.036"))
    tvq_taux_rapide: Mapped[Decimal] = mapped_column(Numeric(8, 5), nullable=False, default=Decimal("0.066"))
    rabais_rapide_taux: Mapped[Decimal] = mapped_column(Numeric(8, 5), nullable=False, default=Decimal("0.01"))
    rabais_rapide_plafond: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("30000"))
    redevance_par_course: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=Decimal("0.90"))
