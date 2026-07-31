from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.route import Route


class Airline(Base):
    __tablename__ = "airlines"

    icao: Mapped[str] = mapped_column(String(3), primary_key=True)
    iata: Mapped[str | None] = mapped_column(String(2), index=True)
    name: Mapped[str]
    callsign: Mapped[str]
    country: Mapped[str]
    has_logo: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")

    routes: Mapped[list["Route"]] = relationship(back_populates="airline")

    def __repr__(self) -> str:
        return f"<Airline {self.icao}>"

    @property
    def logo_path(self) -> str | None:
        """Relative path to this airline's logo under data/logos/, if one exists."""
        return f"data/logos/{self.icao}.png" if self.has_logo else None
