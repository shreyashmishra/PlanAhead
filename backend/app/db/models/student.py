from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.elective_selection import ElectiveSelection
    from app.db.models.student_course_progress import StudentCourseProgress


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)

    course_progresses: Mapped[list["StudentCourseProgress"]] = relationship(back_populates="student")
    elective_selections: Mapped[list["ElectiveSelection"]] = relationship(back_populates="student")
