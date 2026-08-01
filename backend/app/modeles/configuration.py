from sqlalchemy import Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Configuration(Base):
    __tablename__ = "configuration"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    redevance_prelevee_source: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
