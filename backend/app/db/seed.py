from __future__ import annotations

import argparse

from sqlalchemy import delete, select

from app.db.models.course import Course
from app.db.models.elective_group import ElectiveGroup
from app.db.models.elective_selection import ElectiveSelection
from app.db.models.prerequisite_rule import PrerequisiteRule
from app.db.models.program import Program
from app.db.models.program_plan_template import ProgramPlanTemplate
from app.db.models.program_requirement import ProgramRequirement
from app.db.models.requirement_group import RequirementGroup
from app.db.models.student import Student
from app.db.models.student_course_progress import StudentCourseProgress
from app.db.models.term import Term
from app.db.models.university import University
from app.db.session import SessionLocal
from app.modules.universities.common.requirement_types import CourseRequirementDefinition, CourseStatus, RequirementKind
from app.modules.universities.waterloo.programs import PROGRAM_BUILDERS


def seed_database(reset_programs: bool = False) -> None:
    with SessionLocal() as session:
        university = session.scalar(select(University).where(University.code == "WATERLOO"))
        if university is None:
            university = University(code="WATERLOO", name="University of Waterloo")
            session.add(university)
            session.commit()
            session.refresh(university)

        for program_code in ("CS",):
            program_definition = PROGRAM_BUILDERS[program_code]()
            existing_program = session.scalar(
                select(Program).where(
                    Program.university_id == university.id,
                    Program.code == program_definition.program_code,
                )
            )
            if existing_program is not None and reset_programs:
                session.execute(delete(ElectiveSelection).where(ElectiveSelection.program_id == existing_program.id))
                session.execute(delete(StudentCourseProgress).where(StudentCourseProgress.program_id == existing_program.id))
                session.delete(existing_program)
                session.commit()
                existing_program = None

            if existing_program is not None:
                continue

            course_cache: dict[str, Course] = {}
            for course_definition in _iter_courses(program_definition):
                course = session.scalar(
                    select(Course).where(Course.university_id == university.id, Course.code == course_definition.course.code)
                )
                if course is None:
                    course = Course(
                        university_id=university.id,
                        code=course_definition.course.code,
                        title=course_definition.course.title,
                        subject=course_definition.course.subject or course_definition.course.code.split()[0],
                        credits=course_definition.course.credits,
                        description=course_definition.course.description,
                    )
                    session.add(course)
                    session.flush()
                course_cache[course.code] = course

            program = Program(
                university_id=university.id,
                code=program_definition.program_code,
                name=program_definition.name,
                degree=program_definition.degree,
                description=program_definition.description,
            )
            session.add(program)
            session.flush()

            plan_template = ProgramPlanTemplate(
                program_id=program.id,
                title=f"{program_definition.name} Roadmap",
                version="2026.1",
            )
            session.add(plan_template)
            session.flush()

            group_cache: dict[str, ElectiveGroup] = {}

            for term_definition in program_definition.terms:
                term = Term(
                    program_plan_template_id=plan_template.id,
                    code=term_definition.code,
                    label=term_definition.label,
                    year=term_definition.year,
                    season=term_definition.season,
                    sequence=term_definition.sequence,
                )
                session.add(term)
                session.flush()

                for requirement in term_definition.requirements:
                    if requirement.course is not None:
                        session.add(
                            ProgramRequirement(
                                program_id=program.id,
                                term_id=term.id,
                                requirement_group_id=None,
                                course_id=course_cache[requirement.course.course.code].id,
                                requirement_type=RequirementKind.COURSE,
                                sequence=requirement.sequence,
                                display_title=requirement.course.code,
                                notes=requirement.course.notes,
                                is_recommended=True,
                            )
                        )

                    if requirement.group is not None:
                        group = RequirementGroup(
                            program_id=program.id,
                            term_id=term.id,
                            code=requirement.group.code,
                            title=requirement.group.title,
                            description=requirement.group.description,
                            kind=requirement.group.kind,
                            sequence=requirement.group.sequence,
                            min_selections=requirement.group.min_selections,
                            max_selections=requirement.group.max_selections,
                        )
                        session.add(group)
                        session.flush()

                        elective_group = ElectiveGroup(
                            requirement_group_id=group.id,
                            selection_label=requirement.group.description,
                            credits_required=0.5,
                        )
                        session.add(elective_group)
                        session.flush()
                        group_cache[group.code] = elective_group

                        for option in requirement.group.options:
                            session.add(
                                ProgramRequirement(
                                    program_id=program.id,
                                    term_id=term.id,
                                    requirement_group_id=group.id,
                                    course_id=course_cache[option.course.code].id,
                                    requirement_type=RequirementKind.ELECTIVE_GROUP,
                                    sequence=option.sequence,
                                    display_title=option.course.code,
                                    notes=option.notes,
                                    is_recommended=True,
                                )
                            )

            session.flush()

            existing_prereqs = {
                (row.course_id, row.prerequisite_course_id, row.is_corequisite)
                for row in session.scalars(select(PrerequisiteRule)).all()
            }
            for course_definition in _iter_courses(program_definition):
                course = course_cache[course_definition.course.code]
                for prerequisite in course_definition.prerequisites:
                    prereq_course = course_cache[prerequisite.course_code]
                    key = (course.id, prereq_course.id, prerequisite.is_corequisite)
                    if key in existing_prereqs:
                        continue
                    session.add(
                        PrerequisiteRule(
                            course_id=course.id,
                            prerequisite_course_id=prereq_course.id,
                            minimum_grade=prerequisite.minimum_grade,
                            is_corequisite=prerequisite.is_corequisite,
                        )
                    )

            student = session.scalar(select(Student).where(Student.external_key == "local-demo-user"))
            if student is None:
                student = Student(
                    external_key="local-demo-user",
                    full_name="Demo Student",
                    email="demo.student@planahead.local",
                )
                session.add(student)
                session.flush()

            demo_progress = {
                "CS 135": CourseStatus.COMPLETED,
                "MATH 135": CourseStatus.COMPLETED,
                "MATH 137": CourseStatus.COMPLETED,
                "COMMST 100": CourseStatus.COMPLETED,
                "ECON 101": CourseStatus.COMPLETED,
                "CS 136": CourseStatus.IN_PROGRESS,
                "MATH 136": CourseStatus.IN_PROGRESS,
                "STAT 230": CourseStatus.IN_PROGRESS,
                "PHYS 121": CourseStatus.PLANNED,
                "CS 245": CourseStatus.PLANNED,
                "CS 246": CourseStatus.PLANNED,
            }

            for course_code, status in demo_progress.items():
                session.add(
                    StudentCourseProgress(
                        student_id=student.id,
                        program_id=program.id,
                        course_id=course_cache[course_code].id,
                        status=status,
                    )
                )

            session.add(
                ElectiveSelection(
                    student_id=student.id,
                    program_id=program.id,
                    elective_group_id=group_cache["Y1_FALL_BREADTH"].id,
                    course_id=course_cache["ECON 101"].id,
                )
            )
            session.add(
                ElectiveSelection(
                    student_id=student.id,
                    program_id=program.id,
                    elective_group_id=group_cache["Y1_WINTER_SCIENCE"].id,
                    course_id=course_cache["PHYS 121"].id,
                )
            )

            session.commit()


def _iter_courses(program_definition) -> list[CourseRequirementDefinition]:
    entries: list[CourseRequirementDefinition] = []
    seen: set[str] = set()
    for term in program_definition.terms:
        for requirement in term.requirements:
            if requirement.course is not None and requirement.course.course.code not in seen:
                seen.add(requirement.course.course.code)
                entries.append(requirement.course)
            if requirement.group is not None:
                for option in requirement.group.options:
                    if option.course.code not in seen:
                        seen.add(option.course.code)
                        entries.append(option)
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the PlanAhead database.")
    parser.add_argument("--reset-programs", action="store_true", help="Delete and recreate seeded programs before loading data.")
    args = parser.parse_args()
    seed_database(reset_programs=args.reset_programs)


if __name__ == "__main__":
    main()
