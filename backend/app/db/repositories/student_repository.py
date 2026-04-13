from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.db.models.course import Course
from app.db.models.elective_group import ElectiveGroup
from app.db.models.elective_selection import ElectiveSelection
from app.db.models.program import Program
from app.db.models.program_requirement import ProgramRequirement
from app.db.models.requirement_group import RequirementGroup
from app.db.models.student import Student
from app.db.models.student_course_progress import StudentCourseProgress
from app.db.models.university import University
from app.modules.universities.common.requirement_types import CourseStatus, ProgressSnapshot


class StudentRepository:
    DEMO_STUDENT_KEY = "local-demo-user"

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_progress_snapshot(
        self,
        university_code: str,
        program_code: str,
        student_external_key: str = DEMO_STUDENT_KEY,
    ) -> ProgressSnapshot:
        student = self._get_or_create_student(student_external_key)
        program = self._get_program(university_code, program_code)

        progress_rows = self.session.scalars(
            select(StudentCourseProgress)
            .where(
                StudentCourseProgress.student_id == student.id,
                StudentCourseProgress.program_id == program.id,
            )
            .join(StudentCourseProgress.course)
        ).all()

        selection_rows = self.session.scalars(
            select(ElectiveSelection)
            .where(
                ElectiveSelection.student_id == student.id,
                ElectiveSelection.program_id == program.id,
            )
            .join(ElectiveSelection.course)
            .join(ElectiveSelection.elective_group)
            .join(ElectiveGroup.requirement_group)
        ).all()

        return ProgressSnapshot(
            course_statuses={row.course.code: row.status for row in progress_rows},
            elective_selections={row.elective_group.requirement_group.code: row.course.code for row in selection_rows},
        )

    def update_course_status(
        self,
        university_code: str,
        program_code: str,
        course_code: str,
        status: CourseStatus,
        student_external_key: str = DEMO_STUDENT_KEY,
    ) -> ProgressSnapshot:
        student = self._get_or_create_student(student_external_key)
        program = self._get_program(university_code, program_code)
        course = self._get_course(university_code, course_code)

        existing = self.session.scalar(
            select(StudentCourseProgress).where(
                StudentCourseProgress.student_id == student.id,
                StudentCourseProgress.program_id == program.id,
                StudentCourseProgress.course_id == course.id,
            )
        )

        if status == CourseStatus.NOT_STARTED:
            if existing is not None:
                self.session.delete(existing)
        else:
            if existing is None:
                existing = StudentCourseProgress(
                    student_id=student.id,
                    program_id=program.id,
                    course_id=course.id,
                    status=status,
                )
                self.session.add(existing)
            else:
                existing.status = status

        self.session.commit()
        return self.get_progress_snapshot(university_code, program_code, student_external_key)

    def select_elective(
        self,
        university_code: str,
        program_code: str,
        group_code: str,
        course_code: str,
        student_external_key: str = DEMO_STUDENT_KEY,
    ) -> ProgressSnapshot:
        student = self._get_or_create_student(student_external_key)
        program = self._get_program(university_code, program_code)
        elective_group = self._get_elective_group(program.id, group_code)
        course = self._get_course(university_code, course_code)

        valid_option = self.session.scalar(
            select(ProgramRequirement.id).where(
                ProgramRequirement.requirement_group_id == elective_group.requirement_group_id,
                ProgramRequirement.course_id == course.id,
            )
        )
        if valid_option is None:
            option_course_codes = {requirement.course.code for requirement in elective_group.requirement_group.requirements}
            raise ValueError(f"{course_code} is not a valid option for {group_code}. Options: {sorted(option_course_codes)}")

        existing = self.session.scalar(
            select(ElectiveSelection).where(
                ElectiveSelection.student_id == student.id,
                ElectiveSelection.program_id == program.id,
                ElectiveSelection.elective_group_id == elective_group.id,
            )
        )

        if existing is None:
            existing = ElectiveSelection(
                student_id=student.id,
                program_id=program.id,
                elective_group_id=elective_group.id,
                course_id=course.id,
            )
            self.session.add(existing)
        else:
            existing.course_id = course.id

        self.session.commit()
        return self.get_progress_snapshot(university_code, program_code, student_external_key)

    def clear_elective_selection(
        self,
        university_code: str,
        program_code: str,
        group_code: str,
        student_external_key: str = DEMO_STUDENT_KEY,
    ) -> ProgressSnapshot:
        student = self._get_or_create_student(student_external_key)
        program = self._get_program(university_code, program_code)
        elective_group = self._get_elective_group(program.id, group_code)

        self.session.execute(
            delete(ElectiveSelection).where(
                ElectiveSelection.student_id == student.id,
                ElectiveSelection.program_id == program.id,
                ElectiveSelection.elective_group_id == elective_group.id,
            )
        )
        self.session.commit()
        return self.get_progress_snapshot(university_code, program_code, student_external_key)

    def _get_or_create_student(self, student_external_key: str) -> Student:
        student = self.session.scalar(select(Student).where(Student.external_key == student_external_key))
        if student is None:
            student = Student(
                external_key=student_external_key,
                full_name="Demo Student",
                email="demo.student@planahead.local",
            )
            self.session.add(student)
            self.session.commit()
            self.session.refresh(student)
        return student

    def _get_program(self, university_code: str, program_code: str) -> Program:
        statement = (
            select(Program)
            .join(Program.university)
            .where(University.code == university_code, Program.code == program_code)
        )
        program = self.session.scalar(statement)
        if program is None:
            raise ValueError(f"Unknown program {university_code}/{program_code}.")
        return program

    def _get_course(self, university_code: str, course_code: str) -> Course:
        statement = (
            select(Course)
            .join(Course.university)
            .where(University.code == university_code, Course.code == course_code)
        )
        course = self.session.scalar(statement)
        if course is None:
            raise ValueError(f"Unknown course {university_code}/{course_code}.")
        return course

    def _get_elective_group(self, program_id: int, group_code: str) -> ElectiveGroup:
        statement = (
            select(ElectiveGroup)
            .join(ElectiveGroup.requirement_group)
            .options(
                selectinload(ElectiveGroup.requirement_group)
                .selectinload(RequirementGroup.requirements)
                .selectinload(ProgramRequirement.course)
            )
            .where(RequirementGroup.program_id == program_id, RequirementGroup.code == group_code)
        )
        elective_group = self.session.scalar(statement)
        if elective_group is None:
            raise ValueError(f"Unknown elective group {group_code}.")
        return elective_group
