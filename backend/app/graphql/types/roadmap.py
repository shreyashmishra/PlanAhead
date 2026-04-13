from __future__ import annotations

import strawberry

from app.graphql.types.common import CourseProgressStatus, RequirementGroupKindType, RequirementKindType, TermSeasonType
from app.modules.universities.common.requirement_types import (
    EvaluatedCourse,
    EvaluatedGroup,
    EvaluatedRoadmap,
    EvaluatedTerm,
    EvaluatedTermRequirement,
    RequirementSummary,
)


@strawberry.type
class UniversityType:
    code: str
    name: str


@strawberry.type
class ProgramType:
    code: str
    name: str
    degree: str
    description: str
    university_code: str


@strawberry.type
class RoadmapCourseType:
    code: str
    title: str
    credits: float
    description: str | None
    subject: str | None
    status: CourseProgressStatus
    prerequisites_met: bool
    prerequisite_message: str | None
    notes: str | None
    is_selected: bool


@strawberry.type
class ElectiveGroupType:
    code: str
    title: str
    description: str
    kind: RequirementGroupKindType
    min_selections: int
    max_selections: int
    selected_course_code: str | None
    status: CourseProgressStatus
    is_satisfied: bool
    notes: str | None
    options: list[RoadmapCourseType]


@strawberry.type
class TermRequirementType:
    kind: RequirementKindType
    sequence: int
    course: RoadmapCourseType | None
    group: ElectiveGroupType | None


@strawberry.type
class RequirementSummaryType:
    total_requirements: int
    completed_requirements: int
    in_progress_requirements: int
    planned_requirements: int
    remaining_requirements: int
    selected_electives: int
    completion_percentage: float


@strawberry.type
class TermRoadmapType:
    code: str
    label: str
    year: int
    season: TermSeasonType
    sequence: int
    completed_count: int
    total_count: int
    requirements: list[TermRequirementType]


@strawberry.type
class RoadmapType:
    university_code: str
    program_code: str
    program_name: str
    degree: str
    description: str
    summary: RequirementSummaryType
    terms: list[TermRoadmapType]


def map_university(university) -> UniversityType:
    return UniversityType(code=university.code, name=university.name)


def map_program(program) -> ProgramType:
    return ProgramType(
        code=program.code,
        name=program.name,
        degree=program.degree,
        description=program.description,
        university_code=program.university.code,
    )


def map_roadmap_course(course: EvaluatedCourse) -> RoadmapCourseType:
    return RoadmapCourseType(
        code=course.code,
        title=course.title,
        credits=course.credits,
        description=course.description,
        subject=course.subject,
        status=course.status,
        prerequisites_met=course.prerequisites_met,
        prerequisite_message=course.prerequisite_message,
        notes=course.notes,
        is_selected=course.is_selected,
    )


def map_group(group: EvaluatedGroup) -> ElectiveGroupType:
    return ElectiveGroupType(
        code=group.code,
        title=group.title,
        description=group.description,
        kind=group.kind,
        min_selections=group.min_selections,
        max_selections=group.max_selections,
        selected_course_code=group.selected_course_code,
        status=group.status,
        is_satisfied=group.is_satisfied,
        notes=group.notes,
        options=[map_roadmap_course(option) for option in group.options],
    )


def map_term_requirement(requirement: EvaluatedTermRequirement) -> TermRequirementType:
    return TermRequirementType(
        kind=requirement.kind,
        sequence=requirement.sequence,
        course=map_roadmap_course(requirement.course) if requirement.course else None,
        group=map_group(requirement.group) if requirement.group else None,
    )


def map_summary(summary: RequirementSummary) -> RequirementSummaryType:
    return RequirementSummaryType(
        total_requirements=summary.total_requirements,
        completed_requirements=summary.completed_requirements,
        in_progress_requirements=summary.in_progress_requirements,
        planned_requirements=summary.planned_requirements,
        remaining_requirements=summary.remaining_requirements,
        selected_electives=summary.selected_electives,
        completion_percentage=summary.completion_percentage,
    )


def map_term(term: EvaluatedTerm) -> TermRoadmapType:
    return TermRoadmapType(
        code=term.code,
        label=term.label,
        year=term.year,
        season=term.season,
        sequence=term.sequence,
        completed_count=term.completed_count,
        total_count=term.total_count,
        requirements=[map_term_requirement(requirement) for requirement in term.requirements],
    )


def map_roadmap(roadmap: EvaluatedRoadmap) -> RoadmapType:
    return RoadmapType(
        university_code=roadmap.university_code,
        program_code=roadmap.program_code,
        program_name=roadmap.program_name,
        degree=roadmap.degree,
        description=roadmap.description,
        summary=map_summary(roadmap.summary),
        terms=[map_term(term) for term in roadmap.terms],
    )
