from __future__ import annotations

import strawberry

from app.graphql.types.common import CourseProgressStatus, ProgressInput
from app.modules.universities.common.requirement_types import ProgressSnapshot


@strawberry.type
class CourseProgressEntryType:
    course_code: str
    status: CourseProgressStatus


@strawberry.type
class ElectiveSelectionRecordType:
    group_code: str
    course_code: str


@strawberry.type
class StudentProgressType:
    student_external_key: str
    course_statuses: list[CourseProgressEntryType]
    elective_selections: list[ElectiveSelectionRecordType]


def progress_input_to_snapshot(progress_input: ProgressInput | None) -> ProgressSnapshot:
    if progress_input is None:
        return ProgressSnapshot()

    return ProgressSnapshot(
        course_statuses={entry.course_code: entry.status for entry in progress_input.course_statuses},
        elective_selections={entry.group_code: entry.course_code for entry in progress_input.elective_selections},
    )


def map_student_progress(snapshot: ProgressSnapshot, student_external_key: str) -> StudentProgressType:
    return StudentProgressType(
        student_external_key=student_external_key,
        course_statuses=[
            CourseProgressEntryType(course_code=course_code, status=status)
            for course_code, status in sorted(snapshot.course_statuses.items())
        ],
        elective_selections=[
            ElectiveSelectionRecordType(group_code=group_code, course_code=course_code)
            for group_code, course_code in sorted(snapshot.elective_selections.items())
        ],
    )
