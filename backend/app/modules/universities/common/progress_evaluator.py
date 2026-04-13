from __future__ import annotations

from app.modules.universities.common.requirement_types import CourseStatus, RequirementSummary


def summarize_requirement_statuses(statuses: list[CourseStatus], selected_electives: int) -> RequirementSummary:
    total_requirements = len(statuses)
    completed_requirements = sum(1 for status in statuses if status == CourseStatus.COMPLETED)
    in_progress_requirements = sum(1 for status in statuses if status == CourseStatus.IN_PROGRESS)
    planned_requirements = sum(1 for status in statuses if status == CourseStatus.PLANNED)
    remaining_requirements = total_requirements - completed_requirements - in_progress_requirements - planned_requirements
    completion_percentage = round((completed_requirements / total_requirements) * 100, 1) if total_requirements else 0.0

    return RequirementSummary(
        total_requirements=total_requirements,
        completed_requirements=completed_requirements,
        in_progress_requirements=in_progress_requirements,
        planned_requirements=planned_requirements,
        remaining_requirements=remaining_requirements,
        selected_electives=selected_electives,
        completion_percentage=completion_percentage,
    )
