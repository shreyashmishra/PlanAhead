from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.program import Program
    from app.db.models.term import Term


class ProgramPlanTemplate(Base):
    __tablename__ = "program_plan_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id", ondelete="CASCADE"), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(32), default="2026.1")

    program: Mapped["Program"] = relationship(back_populates="plan_template")
    terms: Mapped[list["Term"]] = relationship(
        back_populates="plan_template",
        order_by="Term.sequence",
        cascade="all, delete-orphan",
    )
