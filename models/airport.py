from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.route import Route


class Airport(Base):
    __tablename__ = "airports"

    icao: Mapped[str] = mapped_column(String(4), primary_key=True)
    iata: Mapped[str | None] = mapped_column(String(3), unique=True, index=True)
    name: Mapped[str]
    city: Mapped[str]
    country: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
    timezone: Mapped[str]

    departures: Mapped[list["Route"]] = relationship(
        back_populates="origin",
        foreign_keys="Route.origin_icao",
    )
    arrivals: Mapped[list["Route"]] = relationship(
        back_populates="destination",
        foreign_keys="Route.destination_icao",
    )

    def __repr__(self) -> str:
        return f"<Airport {self.icao}>"
