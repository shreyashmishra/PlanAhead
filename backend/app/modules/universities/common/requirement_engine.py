from __future__ import annotations

from app.modules.universities.common.prerequisite_utils import evaluate_prerequisites
from app.modules.universities.common.progress_evaluator import summarize_requirement_statuses
from app.modules.universities.common.requirement_types import (
    CourseStatus,
    EvaluatedCourse,
    EvaluatedGroup,
    EvaluatedRoadmap,
    EvaluatedTerm,
    EvaluatedTermRequirement,
    ProgressSnapshot,
    ProgramDefinition,
    RequirementKind,
)


class RequirementEngine:
    """Shared roadmap evaluator for program definitions across universities."""

    def evaluate(self, program: ProgramDefinition, progress: ProgressSnapshot) -> EvaluatedRoadmap:
        evaluated_terms: list[EvaluatedTerm] = []
        requirement_statuses: list[CourseStatus] = []

        for term in sorted(program.terms, key=lambda item: item.sequence):
            evaluated_requirements: list[EvaluatedTermRequirement] = []
            term_statuses: list[CourseStatus] = []

            for requirement in sorted(term.requirements, key=lambda item: item.sequence):
                if requirement.kind == RequirementKind.COURSE and requirement.course is not None:
                    evaluated_course = self._evaluate_course(requirement.course, progress)
                    evaluated_requirements.append(
                        EvaluatedTermRequirement(
                            kind=RequirementKind.COURSE,
                            sequence=requirement.sequence,
                            course=evaluated_course,
                        )
                    )
                    term_statuses.append(evaluated_course.status)
                    requirement_statuses.append(evaluated_course.status)

                if requirement.kind == RequirementKind.ELECTIVE_GROUP and requirement.group is not None:
                    evaluated_group = self._evaluate_group(requirement.group, progress)
                    evaluated_requirements.append(
                        EvaluatedTermRequirement(
                            kind=RequirementKind.ELECTIVE_GROUP,
                            sequence=requirement.sequence,
                            group=evaluated_group,
                        )
                    )
                    term_statuses.append(evaluated_group.status)
                    requirement_statuses.append(evaluated_group.status)

            evaluated_terms.append(
                EvaluatedTerm(
                    code=term.code,
                    label=term.label,
                    year=term.year,
                    season=term.season,
                    sequence=term.sequence,
                    completed_count=sum(1 for status in term_statuses if status == CourseStatus.COMPLETED),
                    total_count=len(term_statuses),
                    requirements=evaluated_requirements,
                )
            )

        summary = summarize_requirement_statuses(
            requirement_statuses,
            selected_electives=len(progress.elective_selections),
        )

        return EvaluatedRoadmap(
            university_code=program.university_code,
            program_code=program.program_code,
            program_name=program.name,
            degree=program.degree,
            description=program.description,
            summary=summary,
            terms=evaluated_terms,
        )

    def _evaluate_course(self, requirement, progress: ProgressSnapshot) -> EvaluatedCourse:
        status = progress.course_statuses.get(requirement.course.code, CourseStatus.NOT_STARTED)
        prerequisites_met, prerequisite_message = evaluate_prerequisites(
            requirement.prerequisites,
            progress.course_statuses,
        )

        return EvaluatedCourse(
            code=requirement.course.code,
            title=requirement.course.title,
            credits=requirement.course.credits,
            description=requirement.course.description,
            subject=requirement.course.subject,
            status=status,
            prerequisites_met=prerequisites_met,
            prerequisite_message=prerequisite_message,
            notes=requirement.notes,
        )

    def _evaluate_group(self, group, progress: ProgressSnapshot) -> EvaluatedGroup:
        selected_course_code = progress.elective_selections.get(group.code)
        evaluated_options: list[EvaluatedCourse] = []
        selected_status = CourseStatus.NOT_STARTED

        for option in group.options:
            option_status = progress.course_statuses.get(option.course.code, CourseStatus.NOT_STARTED)
            prerequisites_met, prerequisite_message = evaluate_prerequisites(
                option.prerequisites,
                progress.course_statuses,
            )
            is_selected = selected_course_code == option.course.code
            if is_selected:
                selected_status = option_status

            evaluated_options.append(
                EvaluatedCourse(
                    code=option.course.code,
                    title=option.course.title,
                    credits=option.course.credits,
                    description=option.course.description,
                    subject=option.course.subject,
                    status=option_status,
                    prerequisites_met=prerequisites_met,
                    prerequisite_message=prerequisite_message,
                    notes=option.notes,
                    is_selected=is_selected,
                )
            )

        return EvaluatedGroup(
            code=group.code,
            title=group.title,
            description=group.description,
            kind=group.kind,
            min_selections=group.min_selections,
            max_selections=group.max_selections,
            selected_course_code=selected_course_code,
            status=selected_status,
            is_satisfied=selected_course_code is not None and selected_status != CourseStatus.NOT_STARTED,
            notes=group.notes,
            options=evaluated_options,
        )
