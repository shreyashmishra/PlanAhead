from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import RequirementKind

if TYPE_CHECKING:
    from app.db.models.course import Course
    from app.db.models.program import Program
    from app.db.models.requirement_group import RequirementGroup
    from app.db.models.term import Term


class ProgramRequirement(Base):
    __tablename__ = "program_requirements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"), index=True)
    requirement_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("requirement_groups.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    requirement_type: Mapped[RequirementKind] = mapped_column(Enum(RequirementKind, native_enum=False))
    sequence: Mapped[int] = mapped_column(index=True)
    display_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=True)

    program: Mapped["Program"] = relationship(back_populates="requirements")
    term: Mapped["Term"] = relationship(back_populates="requirements")
    requirement_group: Mapped["RequirementGroup | None"] = relationship(back_populates="requirements")
    course: Mapped["Course"] = relationship(back_populates="requirement_entries")
