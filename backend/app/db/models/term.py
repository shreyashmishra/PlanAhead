from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import TermSeason

if TYPE_CHECKING:
    from app.db.models.program_plan_template import ProgramPlanTemplate
    from app.db.models.program_requirement import ProgramRequirement
    from app.db.models.requirement_group import RequirementGroup


class Term(Base):
    __tablename__ = "terms"
    __table_args__ = (UniqueConstraint("program_plan_template_id", "code", name="uq_term_template_code"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_plan_template_id: Mapped[int] = mapped_column(
        ForeignKey("program_plan_templates.id", ondelete="CASCADE"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(64), index=True)
    label: Mapped[str] = mapped_column(String(255))
    year: Mapped[int]
    season: Mapped[TermSeason] = mapped_column(Enum(TermSeason, native_enum=False))
    sequence: Mapped[int] = mapped_column(index=True)

    plan_template: Mapped["ProgramPlanTemplate"] = relationship(back_populates="terms")
    requirements: Mapped[list["ProgramRequirement"]] = relationship(back_populates="term")
    requirement_groups: Mapped[list["RequirementGroup"]] = relationship(back_populates="term")
