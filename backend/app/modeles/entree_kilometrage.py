from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EntreeKilometrage(Base):
    __tablename__ = "entrees_kilometrage"
    __table_args__ = (UniqueConstraint("periode_id", "date", name="uq_km_periode_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    periode_id: Mapped[int] = mapped_column(ForeignKey("periodes.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    odometre_debut: Mapped[Decimal] = mapped_column(Numeric(12, 1), nullable=False)
    odometre_fin: Mapped[Decimal] = mapped_column(Numeric(12, 1), nullable=False)
    km_professionnels: Mapped[Decimal] = mapped_column(Numeric(12, 1), nullable=False)

    periode: Mapped["Periode"] = relationship(back_populates="entrees_kilometrage")


from app.modeles.periode import Periode  # noqa: E402
