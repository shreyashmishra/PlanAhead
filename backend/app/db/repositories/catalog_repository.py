from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.course import Course
from app.db.models.prerequisite_rule import PrerequisiteRule
from app.db.models.program import Program
from app.db.models.program_plan_template import ProgramPlanTemplate
from app.db.models.program_requirement import ProgramRequirement
from app.db.models.requirement_group import RequirementGroup
from app.db.models.term import Term
from app.db.models.university import University
from app.modules.universities.common.requirement_types import (
    CourseDefinition,
    CourseRequirementDefinition,
    ElectiveGroupDefinition,
    PrerequisiteDefinition,
    ProgramDefinition,
    RequirementKind,
    TermDefinition,
    TermRequirementDefinition,
)


class CatalogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_universities(self) -> list[University]:
        statement = select(University).order_by(University.name.asc())
        return list(self.session.scalars(statement).all())

    def list_programs_by_university(self, university_code: str) -> list[Program]:
        statement = (
            select(Program)
            .join(Program.university)
            .where(University.code == university_code)
            .options(selectinload(Program.university))
            .order_by(Program.name.asc())
        )
        return list(self.session.scalars(statement).all())

    def get_program_definition(self, university_code: str, program_code: str) -> ProgramDefinition:
        statement = (
            select(Program)
            .join(Program.university)
            .where(University.code == university_code, Program.code == program_code)
            .options(
                selectinload(Program.university),
                selectinload(Program.plan_template)
                .selectinload(ProgramPlanTemplate.terms)
                .selectinload(Term.requirements)
                .selectinload(ProgramRequirement.course)
                .selectinload(Course.prerequisite_rules)
                .selectinload(PrerequisiteRule.prerequisite_course),
                selectinload(Program.plan_template)
                .selectinload(ProgramPlanTemplate.terms)
                .selectinload(Term.requirement_groups)
                .selectinload(RequirementGroup.requirements)
                .selectinload(ProgramRequirement.course)
                .selectinload(Course.prerequisite_rules)
                .selectinload(PrerequisiteRule.prerequisite_course),
                selectinload(Program.plan_template)
                .selectinload(ProgramPlanTemplate.terms)
                .selectinload(Term.requirement_groups)
                .selectinload(RequirementGroup.elective_group),
            )
        )
        program = self.session.scalar(statement)
        if program is None or program.plan_template is None:
            raise ValueError(f"Program {university_code}/{program_code} is not available.")

        terms: list[TermDefinition] = []
        for term in sorted(program.plan_template.terms, key=lambda item: item.sequence):
            term_requirements: list[TermRequirementDefinition] = []

            for requirement in sorted(
                [item for item in term.requirements if item.requirement_group_id is None],
                key=lambda item: item.sequence,
            ):
                term_requirements.append(
                    TermRequirementDefinition(
                        kind=requirement.requirement_type,
                        sequence=requirement.sequence,
                        course=self._build_course_requirement(requirement),
                    )
                )

            for group in sorted(term.requirement_groups, key=lambda item: item.sequence):
                term_requirements.append(
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=group.sequence,
                        group=self._build_group(group),
                    )
                )

            term_requirements.sort(key=lambda item: item.sequence)
            terms.append(
                TermDefinition(
                    code=term.code,
                    label=term.label,
                    year=term.year,
                    season=term.season,
                    sequence=term.sequence,
                    requirements=term_requirements,
                )
            )

        return ProgramDefinition(
            university_code=program.university.code,
            program_code=program.code,
            name=program.name,
            degree=program.degree,
            description=program.description,
            terms=terms,
        )

    def _build_group(self, group: RequirementGroup) -> ElectiveGroupDefinition:
        return ElectiveGroupDefinition(
            code=group.code,
            title=group.title,
            description=group.description,
            kind=group.kind,
            min_selections=group.min_selections,
            max_selections=group.max_selections,
            sequence=group.sequence,
            options=[self._build_course_requirement(requirement) for requirement in sorted(group.requirements, key=lambda item: item.sequence)],
            notes=group.elective_group.selection_label if group.elective_group else None,
        )

    def _build_course_requirement(self, requirement: ProgramRequirement) -> CourseRequirementDefinition:
        course = requirement.course
        return CourseRequirementDefinition(
            code=requirement.display_title or course.code.replace(" ", "_"),
            course=CourseDefinition(
                code=course.code,
                title=course.title,
                credits=course.credits,
                description=course.description,
                subject=course.subject,
            ),
            sequence=requirement.sequence,
            notes=requirement.notes,
            prerequisites=[
                PrerequisiteDefinition(
                    course_code=rule.prerequisite_course.code,
                    minimum_grade=rule.minimum_grade,
                    is_corequisite=rule.is_corequisite,
                )
                for rule in sorted(course.prerequisite_rules, key=lambda item: item.prerequisite_course.code)
            ],
            kind=requirement.requirement_type,
        )
