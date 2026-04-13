from __future__ import annotations

from app.modules.universities.common.requirement_types import (
    CourseDefinition,
    CourseRequirementDefinition,
    ProgramDefinition,
    RequirementKind,
    TermDefinition,
    TermRequirementDefinition,
    TermSeason,
)


def _course(code: str, title: str, subject: str) -> CourseDefinition:
    return CourseDefinition(code=code, title=title, subject=subject, credits=0.5)


def build_math_program_definition() -> ProgramDefinition:
    return ProgramDefinition(
        university_code="WATERLOO",
        program_code="MATH",
        name="Mathematics",
        degree="Bachelor of Mathematics",
        description="Extension placeholder for a future Waterloo Mathematics roadmap.",
        terms=[
            TermDefinition(
                code="Y1_FALL",
                label="Year 1 Fall",
                year=1,
                season=TermSeason.FALL,
                sequence=1,
                requirements=[
                    TermRequirementDefinition(
                        kind=RequirementKind.COURSE,
                        sequence=1,
                        course=CourseRequirementDefinition(
                            code="MATH_135",
                            course=_course("MATH 135", "Algebra for Honours Mathematics", "MATH"),
                            sequence=1,
                        ),
                    ),
                    TermRequirementDefinition(
                        kind=RequirementKind.COURSE,
                        sequence=2,
                        course=CourseRequirementDefinition(
                            code="MATH_137",
                            course=_course("MATH 137", "Calculus 1", "MATH"),
                            sequence=2,
                        ),
                    ),
                ],
            ),
        ],
    )
