from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Revenu(Base):
    __tablename__ = "revenus"
    __table_args__ = (UniqueConstraint("periode_id", "date", name="uq_revenu_periode_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    periode_id: Mapped[int] = mapped_column(ForeignKey("periodes.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    nombre_courses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenu_brut: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    pourboires: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    periode: Mapped["Periode"] = relationship(back_populates="revenus")


from app.modeles.periode import Periode  # noqa: E402
