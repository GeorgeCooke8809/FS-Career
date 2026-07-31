from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.route import Route


class Airline(Base):
    __tablename__ = "airlines"

    icao: Mapped[str] = mapped_column(String(3), primary_key=True)
    iata: Mapped[str | None] = mapped_column(String(2), unique=True, index=True)
    name: Mapped[str]
    callsign: Mapped[str]
    country: Mapped[str]

    routes: Mapped[list["Route"]] = relationship(back_populates="airline")

    def __repr__(self) -> str:
        return f"<Airline {self.icao}>"
