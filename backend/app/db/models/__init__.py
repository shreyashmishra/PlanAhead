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

__all__ = [
    "Course",
    "ElectiveGroup",
    "ElectiveSelection",
    "PrerequisiteRule",
    "Program",
    "ProgramPlanTemplate",
    "ProgramRequirement",
    "RequirementGroup",
    "Student",
    "StudentCourseProgress",
    "Term",
    "University",
]
