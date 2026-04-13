from __future__ import annotations

import strawberry
from strawberry.types import Info

from app.graphql.context import DEFAULT_STUDENT_KEY, GraphQLContext
from app.graphql.types.common import ProgressInput
from app.graphql.types.roadmap import (
    ProgramType,
    RequirementSummaryType,
    RoadmapType,
    UniversityType,
    map_program,
    map_roadmap,
    map_summary,
    map_university,
)
from app.graphql.types.student_progress import StudentProgressType, map_student_progress, progress_input_to_snapshot


@strawberry.type
class Query:
    @strawberry.field
    def available_universities(self, info: Info[GraphQLContext, None]) -> list[UniversityType]:
        return [map_university(item) for item in info.context.programs.list_available_universities()]

    @strawberry.field
    def programs_by_university(self, info: Info[GraphQLContext, None], university_code: str) -> list[ProgramType]:
        return [map_program(item) for item in info.context.programs.list_programs_by_university(university_code)]

    @strawberry.field
    def roadmap_by_program(
        self,
        info: Info[GraphQLContext, None],
        university_code: str,
        program_code: str,
        progress_input: ProgressInput | None = None,
    ) -> RoadmapType:
        progress = progress_input_to_snapshot(progress_input)
        roadmap = info.context.programs.get_roadmap(university_code, program_code, progress)
        return map_roadmap(roadmap)

    @strawberry.field
    def student_progress(
        self,
        info: Info[GraphQLContext, None],
        university_code: str,
        program_code: str,
        student_external_key: str = DEFAULT_STUDENT_KEY,
    ) -> StudentProgressType:
        snapshot = info.context.students.get_student_progress(university_code, program_code, student_external_key)
        return map_student_progress(snapshot, student_external_key)

    @strawberry.field
    def requirement_summary(
        self,
        info: Info[GraphQLContext, None],
        university_code: str,
        program_code: str,
        progress_input: ProgressInput | None = None,
    ) -> RequirementSummaryType:
        progress = progress_input_to_snapshot(progress_input)
        summary = info.context.programs.get_requirement_summary(university_code, program_code, progress)
        return map_summary(summary)
