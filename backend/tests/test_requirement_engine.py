from app.modules.universities.common.requirement_types import CourseStatus, ProgressSnapshot
from app.modules.universities.waterloo.programs.computer_science import build_computer_science_program_definition
from app.modules.universities.waterloo.waterloo_requirement_engine import WaterlooRequirementEngine


def test_waterloo_requirement_engine_respects_prerequisites_and_electives():
    program = build_computer_science_program_definition()
    progress = ProgressSnapshot(
        course_statuses={
            "CS 135": CourseStatus.COMPLETED,
            "ECON 101": CourseStatus.PLANNED,
        },
        elective_selections={"Y1_FALL_BREADTH": "ECON 101"},
    )

    roadmap = WaterlooRequirementEngine().evaluate(program, progress)

    assert roadmap.summary.planned_requirements == 1
    assert roadmap.summary.completed_requirements == 1

    year_one_winter = roadmap.terms[1]
    cs_136 = next(
        requirement.course
        for requirement in year_one_winter.requirements
        if requirement.course and requirement.course.code == "CS 136"
    )
    assert cs_136 is not None
    assert cs_136.prerequisites_met is True

    year_one_spring = roadmap.terms[2]
    cs_245 = next(
        requirement.course
        for requirement in year_one_spring.requirements
        if requirement.course and requirement.course.code == "CS 245"
    )
    assert cs_245 is not None
    assert cs_245.prerequisites_met is False

    year_one_fall_group = next(
        requirement.group
        for requirement in roadmap.terms[0].requirements
        if requirement.group and requirement.group.code == "Y1_FALL_BREADTH"
    )
    assert year_one_fall_group is not None
    assert year_one_fall_group.selected_course_code == "ECON 101"
    assert year_one_fall_group.status == CourseStatus.PLANNED
