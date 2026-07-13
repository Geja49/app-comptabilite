from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Periode(Base):
    __tablename__ = "periodes"
    __table_args__ = (UniqueConstraint("annee", "mois", name="uq_periode_annee_mois"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    mois: Mapped[int] = mapped_column(Integer, nullable=False)

    revenus: Mapped[list["Revenu"]] = relationship(back_populates="periode", cascade="all, delete-orphan")
    depenses: Mapped[list["Depense"]] = relationship(back_populates="periode", cascade="all, delete-orphan")
    entrees_kilometrage: Mapped[list["EntreeKilometrage"]] = relationship(
        back_populates="periode", cascade="all, delete-orphan"
    )


from app.modeles.revenu import Revenu  # noqa: E402
from app.modeles.depense import Depense  # noqa: E402
from app.modeles.entree_kilometrage import EntreeKilometrage  # noqa: E402
