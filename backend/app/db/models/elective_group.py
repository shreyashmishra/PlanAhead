from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.elective_selection import ElectiveSelection
    from app.db.models.requirement_group import RequirementGroup


class ElectiveGroup(Base):
    __tablename__ = "elective_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    requirement_group_id: Mapped[int] = mapped_column(
        ForeignKey("requirement_groups.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    selection_label: Mapped[str] = mapped_column(String(255), default="Choose from the following")
    credits_required: Mapped[float] = mapped_column(Float, default=0.5)

    requirement_group: Mapped["RequirementGroup"] = relationship(back_populates="elective_group")
    selections: Mapped[list["ElectiveSelection"]] = relationship(back_populates="elective_group")
