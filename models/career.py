from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.airline import Airline
    from models.airport import Airport
    from models.schedule import Schedule


class Career(Base):
    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    profile_picture_path: Mapped[str]
    base_icao: Mapped[str] = mapped_column(String(4), ForeignKey("airports.icao", onupdate="CASCADE"), index=True)
    rank: Mapped[int] = mapped_column(default=0)
    current_airline_icao: Mapped[str] = mapped_column(String(3), ForeignKey("airlines.icao", onupdate="CASCADE"), index=True)
    bank_balance: Mapped[int] = mapped_column(default=0)
    current_day: Mapped[int] = mapped_column( default=0)

    # Relationships:
    base: Mapped["Airport"] = relationship(back_populates="careers", foreign_keys=[base_icao])
    current_airline: Mapped["Airline"] = relationship(back_populates="careers", foreign_keys=[current_airline_icao])
    schedules: Mapped[list["Schedule"]] = relationship(back_populates="career")

    def __repr__(self) -> str:
        return f"<Career: {self.id = }, {self.name = }, {self.base_icao = }, {self.rank = }, {self.current_airline_icao = }, {self.bank_balance = }, {self.current_day = }>"
