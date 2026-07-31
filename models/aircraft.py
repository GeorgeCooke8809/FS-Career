from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.route import Route


class Aircraft(Base):
    __tablename__ = "aircraft"

    icao_type: Mapped[str] = mapped_column(String(4), primary_key=True)
    name: Mapped[str]
    manufacturer: Mapped[str]

    routes: Mapped[list["Route"]] = relationship(back_populates="aircraft")

    def __repr__(self) -> str:
        return f"<Aircraft {self.icao_type}>"
