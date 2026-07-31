from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
    from models.aircraft import Aircraft
    from models.airline import Airline
    from models.airport import Airport


class Route(Base):
    __tablename__ = "routes"
    __table_args__ = (
        UniqueConstraint("airline_icao", "flight_number", name="uq_route_airline_flight_number"),
        CheckConstraint("distance_nm > 0", name="ck_route_distance_positive"),
        CheckConstraint("duration_minutes > 0", name="ck_route_duration_positive"),
        CheckConstraint("origin_icao != destination_icao", name="ck_route_origin_ne_destination"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    airline_icao: Mapped[str] = mapped_column(
        String(3), ForeignKey("airlines.icao", onupdate="CASCADE"), index=True
    )
    origin_icao: Mapped[str] = mapped_column(
        String(4), ForeignKey("airports.icao", onupdate="CASCADE"), index=True
    )
    destination_icao: Mapped[str] = mapped_column(
        String(4), ForeignKey("airports.icao", onupdate="CASCADE"), index=True
    )
    aircraft_icao_type: Mapped[str] = mapped_column(
        String(4), ForeignKey("aircraft.icao_type", onupdate="CASCADE"), index=True
    )

    flight_number: Mapped[str]
    distance_nm: Mapped[float]
    departure_time_utc: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int]

    airline: Mapped["Airline"] = relationship(back_populates="routes")
    aircraft: Mapped["Aircraft"] = relationship(back_populates="routes")
    origin: Mapped["Airport"] = relationship(
        back_populates="departures", foreign_keys=[origin_icao]
    )
    destination: Mapped["Airport"] = relationship(
        back_populates="arrivals", foreign_keys=[destination_icao]
    )

    def __repr__(self) -> str:
        return f"<Route {self.airline_icao}{self.flight_number} {self.origin_icao}->{self.destination_icao}>"
