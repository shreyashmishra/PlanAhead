from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.course import Course
    from app.db.models.elective_group import ElectiveGroup
    from app.db.models.program import Program
    from app.db.models.student import Student


class ElectiveSelection(Base):
    __tablename__ = "elective_selections"
    __table_args__ = (
        UniqueConstraint("student_id", "program_id", "elective_group_id", name="uq_student_program_elective"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), index=True)
    elective_group_id: Mapped[int] = mapped_column(ForeignKey("elective_groups.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="elective_selections")
    program: Mapped["Program"] = relationship()
    elective_group: Mapped["ElectiveGroup"] = relationship(back_populates="selections")
    course: Mapped["Course"] = relationship()
