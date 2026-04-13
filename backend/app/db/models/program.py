from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.program_plan_template import ProgramPlanTemplate
    from app.db.models.program_requirement import ProgramRequirement
    from app.db.models.requirement_group import RequirementGroup
    from app.db.models.student_course_progress import StudentCourseProgress
    from app.db.models.university import University


class Program(Base):
    __tablename__ = "programs"
    __table_args__ = (UniqueConstraint("university_id", "code", name="uq_program_university_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    degree: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text)

    university: Mapped["University"] = relationship(back_populates="programs")
    plan_template: Mapped["ProgramPlanTemplate"] = relationship(back_populates="program", uselist=False)
    requirement_groups: Mapped[list["RequirementGroup"]] = relationship(back_populates="program")
    requirements: Mapped[list["ProgramRequirement"]] = relationship(back_populates="program")
    course_progresses: Mapped[list["StudentCourseProgress"]] = relationship(back_populates="program")
