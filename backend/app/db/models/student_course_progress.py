from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import CourseStatus

if TYPE_CHECKING:
    from app.db.models.course import Course
    from app.db.models.program import Program
    from app.db.models.student import Student


class StudentCourseProgress(Base):
    __tablename__ = "student_course_progress"
    __table_args__ = (
        UniqueConstraint("student_id", "program_id", "course_id", name="uq_student_program_course_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    status: Mapped[CourseStatus] = mapped_column(Enum(CourseStatus, native_enum=False))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="course_progresses")
    program: Mapped["Program"] = relationship(back_populates="course_progresses")
    course: Mapped["Course"] = relationship(back_populates="student_progresses")
