from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CourseStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class RequirementKind(str, Enum):
    COURSE = "COURSE"
    ELECTIVE_GROUP = "ELECTIVE_GROUP"


class RequirementGroupKind(str, Enum):
    CORE = "CORE"
    ELECTIVE = "ELECTIVE"
    ONE_OF = "ONE_OF"


class TermSeason(str, Enum):
    FALL = "FALL"
    WINTER = "WINTER"
    SPRING = "SPRING"


@dataclass(slots=True)
class CourseDefinition:
    code: str
    title: str
    credits: float = 0.5
    description: str | None = None
    subject: str | None = None


@dataclass(slots=True)
class PrerequisiteDefinition:
    course_code: str
    minimum_grade: str | None = None
    is_corequisite: bool = False


@dataclass(slots=True)
class CourseRequirementDefinition:
    code: str
    course: CourseDefinition
    sequence: int
    notes: str | None = None
    prerequisites: list[PrerequisiteDefinition] = field(default_factory=list)
    kind: RequirementKind = RequirementKind.COURSE


@dataclass(slots=True)
class ElectiveGroupDefinition:
    code: str
    title: str
    description: str
    kind: RequirementGroupKind
    min_selections: int
    max_selections: int
    sequence: int
    options: list[CourseRequirementDefinition]
    notes: str | None = None


@dataclass(slots=True)
class TermRequirementDefinition:
    kind: RequirementKind
    sequence: int
    course: CourseRequirementDefinition | None = None
    group: ElectiveGroupDefinition | None = None


@dataclass(slots=True)
class TermDefinition:
    code: str
    label: str
    year: int
    season: TermSeason
    sequence: int
    requirements: list[TermRequirementDefinition]


@dataclass(slots=True)
class ProgramDefinition:
    university_code: str
    program_code: str
    name: str
    degree: str
    description: str
    terms: list[TermDefinition]


@dataclass(slots=True)
class ProgressSnapshot:
    course_statuses: dict[str, CourseStatus] = field(default_factory=dict)
    elective_selections: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class EvaluatedCourse:
    code: str
    title: str
    credits: float
    description: str | None
    subject: str | None
    status: CourseStatus
    prerequisites_met: bool
    prerequisite_message: str | None
    notes: str | None
    is_selected: bool = True


@dataclass(slots=True)
class EvaluatedGroup:
    code: str
    title: str
    description: str
    kind: RequirementGroupKind
    min_selections: int
    max_selections: int
    selected_course_code: str | None
    status: CourseStatus
    is_satisfied: bool
    notes: str | None
    options: list[EvaluatedCourse]


@dataclass(slots=True)
class EvaluatedTermRequirement:
    kind: RequirementKind
    sequence: int
    course: EvaluatedCourse | None = None
    group: EvaluatedGroup | None = None


@dataclass(slots=True)
class RequirementSummary:
    total_requirements: int
    completed_requirements: int
    in_progress_requirements: int
    planned_requirements: int
    remaining_requirements: int
    selected_electives: int
    completion_percentage: float


@dataclass(slots=True)
class EvaluatedTerm:
    code: str
    label: str
    year: int
    season: TermSeason
    sequence: int
    completed_count: int
    total_count: int
    requirements: list[EvaluatedTermRequirement]


@dataclass(slots=True)
class EvaluatedRoadmap:
    university_code: str
    program_code: str
    program_name: str
    degree: str
    description: str
    summary: RequirementSummary
    terms: list[EvaluatedTerm]
