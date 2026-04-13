from __future__ import annotations

import strawberry

from app.modules.universities.common.requirement_types import CourseStatus, RequirementGroupKind, RequirementKind, TermSeason


CourseProgressStatus = strawberry.enum(CourseStatus, name="CourseProgressStatus")
RequirementKindType = strawberry.enum(RequirementKind, name="RequirementKind")
RequirementGroupKindType = strawberry.enum(RequirementGroupKind, name="RequirementGroupKind")
TermSeasonType = strawberry.enum(TermSeason, name="TermSeason")


@strawberry.input
class CourseStatusInput:
    course_code: str
    status: CourseStatus


@strawberry.input
class ElectiveSelectionInput:
    group_code: str
    course_code: str


@strawberry.input
class ProgressInput:
    course_statuses: list[CourseStatusInput] = strawberry.field(default_factory=list)
    elective_selections: list[ElectiveSelectionInput] = strawberry.field(default_factory=list)
