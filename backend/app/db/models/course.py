from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.prerequisite_rule import PrerequisiteRule
    from app.db.models.program_requirement import ProgramRequirement
    from app.db.models.student_course_progress import StudentCourseProgress
    from app.db.models.university import University


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("university_id", "code", name="uq_course_university_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(64))
    credits: Mapped[float] = mapped_column(Float, default=0.5)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    university: Mapped["University"] = relationship(back_populates="courses")
    requirement_entries: Mapped[list["ProgramRequirement"]] = relationship(back_populates="course")
    student_progresses: Mapped[list["StudentCourseProgress"]] = relationship(back_populates="course")
    prerequisite_rules: Mapped[list["PrerequisiteRule"]] = relationship(
        back_populates="course",
        foreign_keys="PrerequisiteRule.course_id",
    )
    required_for_rules: Mapped[list["PrerequisiteRule"]] = relationship(
        back_populates="prerequisite_course",
        foreign_keys="PrerequisiteRule.prerequisite_course_id",
    )
