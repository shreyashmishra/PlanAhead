from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import RequirementGroupKind

if TYPE_CHECKING:
    from app.db.models.elective_group import ElectiveGroup
    from app.db.models.program import Program
    from app.db.models.program_requirement import ProgramRequirement
    from app.db.models.term import Term


class RequirementGroup(Base):
    __tablename__ = "requirement_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(500))
    kind: Mapped[RequirementGroupKind] = mapped_column(Enum(RequirementGroupKind, native_enum=False))
    sequence: Mapped[int] = mapped_column(index=True)
    min_selections: Mapped[int] = mapped_column(default=1)
    max_selections: Mapped[int] = mapped_column(default=1)

    program: Mapped["Program"] = relationship(back_populates="requirement_groups")
    term: Mapped["Term"] = relationship(back_populates="requirement_groups")
    requirements: Mapped[list["ProgramRequirement"]] = relationship(
        back_populates="requirement_group",
        order_by="ProgramRequirement.sequence",
    )
    elective_group: Mapped["ElectiveGroup"] = relationship(
        back_populates="requirement_group",
        uselist=False,
        cascade="all, delete-orphan",
    )
