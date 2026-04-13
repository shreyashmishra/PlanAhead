from app.modules.universities.waterloo.programs.computer_science import build_computer_science_program_definition
from app.modules.universities.waterloo.programs.math import build_math_program_definition

PROGRAM_BUILDERS = {
    "CS": build_computer_science_program_definition,
    "MATH": build_math_program_definition,
}

__all__ = ["PROGRAM_BUILDERS", "build_computer_science_program_definition", "build_math_program_definition"]
