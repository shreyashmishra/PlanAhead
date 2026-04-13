from __future__ import annotations

from app.modules.universities.common.requirement_types import CourseStatus, PrerequisiteDefinition


READY_STATUSES = {CourseStatus.IN_PROGRESS, CourseStatus.COMPLETED}
COREQUISITE_READY_STATUSES = {
    CourseStatus.PLANNED,
    CourseStatus.IN_PROGRESS,
    CourseStatus.COMPLETED,
}


def evaluate_prerequisites(
    prerequisites: list[PrerequisiteDefinition],
    course_statuses: dict[str, CourseStatus],
) -> tuple[bool, str | None]:
    if not prerequisites:
        return True, None

    unmet: list[str] = []
    for prerequisite in prerequisites:
        status = course_statuses.get(prerequisite.course_code, CourseStatus.NOT_STARTED)
        ready_statuses = COREQUISITE_READY_STATUSES if prerequisite.is_corequisite else READY_STATUSES
        if status not in ready_statuses:
            unmet.append(prerequisite.course_code)

    if not unmet:
        return True, None

    if len(unmet) == 1:
        return False, f"Needs {unmet[0]} before this course."

    missing = ", ".join(unmet[:-1]) + f", and {unmet[-1]}"
    return False, f"Needs {missing} before this course."
