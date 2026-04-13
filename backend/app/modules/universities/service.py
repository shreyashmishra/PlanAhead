from __future__ import annotations

from app.modules.universities.common.requirement_engine import RequirementEngine
from app.modules.universities.waterloo.waterloo_requirement_engine import WaterlooRequirementEngine


def get_requirement_engine(university_code: str) -> RequirementEngine:
    if university_code == "WATERLOO":
        return WaterlooRequirementEngine()
    return RequirementEngine()
