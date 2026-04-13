from __future__ import annotations

import strawberry
from strawberry.types import Info

from app.graphql.context import DEFAULT_STUDENT_KEY, GraphQLContext
from app.graphql.types.common import CourseProgressStatus
from app.graphql.types.student_progress import StudentProgressType, map_student_progress
from app.modules.universities.common.requirement_types import CourseStatus


@strawberry.input
class UpdateCourseStatusInput:
    university_code: str
    program_code: str
    course_code: str
    status: CourseStatus
    student_external_key: str = DEFAULT_STUDENT_KEY


@strawberry.input
class SelectElectiveInput:
    university_code: str
    program_code: str
    group_code: str
    course_code: str
    student_external_key: str = DEFAULT_STUDENT_KEY


@strawberry.input
class ClearElectiveSelectionInput:
    university_code: str
    program_code: str
    group_code: str
    student_external_key: str = DEFAULT_STUDENT_KEY


@strawberry.type
class Mutation:
    @strawberry.mutation
    def update_course_status(self, info: Info[GraphQLContext, None], input: UpdateCourseStatusInput) -> StudentProgressType:
        snapshot = info.context.students.update_course_status(
            university_code=input.university_code,
            program_code=input.program_code,
            course_code=input.course_code,
            status=input.status,
            student_external_key=input.student_external_key,
        )
        return map_student_progress(snapshot, input.student_external_key)

    @strawberry.mutation
    def select_elective(self, info: Info[GraphQLContext, None], input: SelectElectiveInput) -> StudentProgressType:
        snapshot = info.context.students.select_elective(
            university_code=input.university_code,
            program_code=input.program_code,
            group_code=input.group_code,
            course_code=input.course_code,
            student_external_key=input.student_external_key,
        )
        return map_student_progress(snapshot, input.student_external_key)

    @strawberry.mutation
    def clear_elective_selection(
        self,
        info: Info[GraphQLContext, None],
        input: ClearElectiveSelectionInput,
    ) -> StudentProgressType:
        snapshot = info.context.students.clear_elective_selection(
            university_code=input.university_code,
            program_code=input.program_code,
            group_code=input.group_code,
            student_external_key=input.student_external_key,
        )
        return map_student_progress(snapshot, input.student_external_key)
