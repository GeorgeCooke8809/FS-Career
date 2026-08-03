from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import time

from models.base import Base

if TYPE_CHECKING:
    from models.route import Route
    from models.career import Career

STATUS_OPTIONS = ("completed", "current", "future")

class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (UniqueConstraint("career_id", "day_no", "flight_index", name="unique_day_no_and_flight_index"),
                      CheckConstraint(f"status IN {STATUS_OPTIONS}", name="status_valid_option",),
                )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id", onupdate="CASCADE"), index=True)
    day_no: Mapped[int]
    flight_index: Mapped[int]
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", onupdate="CASCADE"), index=True)
    departure_time_utc: Mapped[time]
    status: Mapped[str] # "completed" | "current" | "future"

    # Relationships:
    route: Mapped["Route"] = relationship(back_populates="schedules", foreign_keys=[route_id])
    career: Mapped["Career"] = relationship(back_populates="schedules", foreign_keys=[career_id])


    def __repr__(self) -> str:
        return f"<Schedule Item: {self.id = }, {self.day_no = }, {self.flight_index = }, {self.route_id = }, {self.departure_time_utc = }, {self.status = }>"
