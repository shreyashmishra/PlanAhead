from __future__ import annotations

from app.modules.universities.common.requirement_engine import RequirementEngine
from app.modules.universities.common.requirement_types import EvaluatedRoadmap, ProgramDefinition, ProgressSnapshot


class WaterlooRequirementEngine(RequirementEngine):
    """Waterloo-specific requirement evaluation hooks live here."""

    def evaluate(self, program: ProgramDefinition, progress: ProgressSnapshot) -> EvaluatedRoadmap:
        roadmap = super().evaluate(program, progress)
        roadmap.description = (
            f"{roadmap.description} This roadmap models a recommended Waterloo sequencing pattern and "
            "keeps elective decisions flexible for future co-op or stream variations."
        )
        return roadmap
