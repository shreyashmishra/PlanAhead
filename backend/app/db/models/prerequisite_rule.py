from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.course import Course


class PrerequisiteRule(Base):
    __tablename__ = "prerequisite_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    prerequisite_course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    minimum_grade: Mapped[str | None] = mapped_column(String(16), nullable=True)
    is_corequisite: Mapped[bool] = mapped_column(Boolean, default=False)

    course: Mapped["Course"] = relationship(
        back_populates="prerequisite_rules",
        foreign_keys=[course_id],
    )
    prerequisite_course: Mapped["Course"] = relationship(
        back_populates="required_for_rules",
        foreign_keys=[prerequisite_course_id],
    )
