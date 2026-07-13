from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CategorieDepense(Base):
    __tablename__ = "categories_depense"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    est_systeme: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    depenses: Mapped[list["Depense"]] = relationship(back_populates="categorie")
    depenses_recurrentes: Mapped[list["DepenseRecurrente"]] = relationship(back_populates="categorie")


from app.modeles.depense import Depense  # noqa: E402
from app.modeles.depense_recurrente import DepenseRecurrente  # noqa: E402
