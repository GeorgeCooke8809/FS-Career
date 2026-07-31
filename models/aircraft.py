from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.aircraft_family import AircraftFamily
    from models.route import Route


class Aircraft(Base):
    __tablename__ = "aircraft"

    icao_type: Mapped[str] = mapped_column(String(4), primary_key=True)
    name: Mapped[str]
    family_id: Mapped[int] = mapped_column(ForeignKey("aircraft_families.id"), index=True)

    family: Mapped["AircraftFamily"] = relationship(back_populates="aircraft")
    routes: Mapped[list["Route"]] = relationship(back_populates="aircraft")

    def __repr__(self) -> str:
        return f"<Aircraft {self.icao_type}>"
