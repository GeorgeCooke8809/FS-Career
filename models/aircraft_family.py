from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.aircraft import Aircraft

CATEGORIES = ("mainline_jet", "regional_jet", "turboprop", "business")


class AircraftFamily(Base):
    __tablename__ = "aircraft_families"
    __table_args__ = (
        CheckConstraint(
            f"category IN {CATEGORIES}", name="ck_aircraft_family_category"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    manufacturer: Mapped[str]
    category: Mapped[str]

    aircraft: Mapped[list["Aircraft"]] = relationship(back_populates="family")

    def __repr__(self) -> str:
        return f"<AircraftFamily {self.name}>"
