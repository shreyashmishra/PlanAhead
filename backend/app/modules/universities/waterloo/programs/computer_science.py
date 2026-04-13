from __future__ import annotations

from app.modules.universities.common.requirement_types import (
    CourseDefinition,
    CourseRequirementDefinition,
    ElectiveGroupDefinition,
    PrerequisiteDefinition,
    ProgramDefinition,
    RequirementGroupKind,
    RequirementKind,
    TermDefinition,
    TermRequirementDefinition,
    TermSeason,
)


COURSE_CATALOG: dict[str, tuple[str, str, str]] = {
    "CS 135": ("Designing Functional Programs", "CS", "Introductory functional programming and algorithmic design."),
    "CS 136": ("Elementary Algorithm Design and Data Abstraction", "CS", "Continuation of CS 135 with data abstraction."),
    "CS 240": ("Data Structures and Data Management", "CS", "Core data structures and performance tradeoffs."),
    "CS 241": ("Foundations of Sequential Programs", "CS", "Low-level program structure, compilation, and memory."),
    "CS 245": ("Logic and Computation", "CS", "Discrete logic foundations for computer science."),
    "CS 246": ("Object-Oriented Software Development", "CS", "Object-oriented design and software construction."),
    "CS 251": ("Computer Organization and Design", "CS", "Computer architecture and systems fundamentals."),
    "CS 341": ("Algorithms", "CS", "Algorithm design, analysis, and correctness."),
    "CS 348": ("Introduction to Database Management", "CS", "Data modeling and relational database systems."),
    "CS 349": ("User Interfaces", "CS", "User interface design and interactive systems."),
    "CS 350": ("Operating Systems", "CS", "Concurrency, processes, and operating system internals."),
    "CS 370": ("Numerical Computation", "CS", "Computational methods with numerical analysis."),
    "CS 371": ("Introduction to Computational Mathematics", "CS", "Mathematical computing and numerical modeling."),
    "CS 445": ("Software Requirements Specification and Analysis", "CS", "Structured software requirements and analysis."),
    "CS 454": ("Distributed Systems", "CS", "Distributed systems design and fault tolerance."),
    "CS 458": ("Computer Security and Privacy", "CS", "Security engineering, privacy, and applied cryptography."),
    "CS 475": ("Computational Linear Algebra", "CS", "Advanced linear algebra methods for computing."),
    "CS 486": ("Introduction to Artificial Intelligence", "CS", "AI search, reasoning, and machine learning basics."),
    "CS 490": ("Design Project 1", "CS", "Capstone design and delivery project."),
    "CS 492": ("Social Implications of Computing", "CS", "Ethics and societal effects of software systems."),
    "CS 497": ("Reading Course", "CS", "Independent directed study in computer science."),
    "CS 338": ("Computer Applications in Business", "CS", "Business-oriented software systems."),
    "CS 346": ("Application Development", "CS", "Applied software development in larger systems."),
    "CS 360": ("Introduction to the Theory of Computing", "CS", "Automata, computation, and complexity."),
    "CS 444": ("Compiler Construction", "CS", "Compiler pipelines and runtime systems."),
    "CS 452": ("Real-Time Programming", "CS", "Embedded and real-time software techniques."),
    "CS 479": ("Neural Networks and Deep Learning", "CS", "Modern deep learning fundamentals."),
    "MATH 135": ("Algebra for Honours Mathematics", "MATH", "Foundations of algebra and mathematical reasoning."),
    "MATH 136": ("Linear Algebra 1", "MATH", "Linear systems, vector spaces, and matrices."),
    "MATH 137": ("Calculus 1", "MATH", "Differential calculus for honours mathematics."),
    "MATH 138": ("Calculus 2", "MATH", "Integral calculus and series."),
    "MATH 239": ("Introduction to Combinatorics", "MATH", "Counting, graphs, and combinatorial reasoning."),
    "STAT 230": ("Probability", "STAT", "Discrete and continuous probability for mathematical computing."),
    "STAT 231": ("Statistics", "STAT", "Statistical inference and estimation."),
    "COMMST 100": ("Communication in Mathematics and Computer Science", "COMM", "Communication practices for technical fields."),
    "ECON 101": ("Introduction to Microeconomics", "ECON", "Economic decision-making and market behaviour."),
    "ECON 201": ("Microeconomic Theory", "ECON", "Intermediate microeconomic analysis."),
    "ECON 290": ("Special Topics in Economics", "ECON", "Selected contemporary topics in economics."),
    "PSYCH 101": ("Introductory Psychology", "PSYCH", "Survey of psychological science."),
    "PSYCH 207": ("Cognitive Processes", "PSYCH", "Perception, memory, and cognition."),
    "ENGL 109": ("Introduction to Academic Writing", "ENGL", "Critical writing and argumentation."),
    "ENGL 210F": ("Genres of Creative Writing", "ENGL", "Writing workshop focused on creative genres."),
    "BIOL 130": ("Cell Biology", "BIOL", "Cell structure, genetics, and biological systems."),
    "CHEM 120": ("General Chemistry 1", "CHEM", "Core chemistry concepts for science students."),
    "PHYS 121": ("Mechanics", "PHYS", "Mechanics and introductory physics problem solving."),
    "SPCOM 100": ("Introduction to Speech Communication", "SPCOM", "Foundations of public speaking and communication."),
    "LS 101": ("Introduction to Legal Studies", "LS", "Survey of legal institutions and reasoning."),
    "AFM 101": ("Introduction to Financial Accounting", "AFM", "Accounting and business reporting fundamentals."),
    "BET 100": ("Foundations of Venture Creation", "BET", "Innovation and venture ideation."),
    "HIST 101": ("World History Since 1500", "HIST", "Modern global historical developments."),
    "PHIL 145": ("Critical Thinking", "PHIL", "Argument analysis and logical reasoning."),
    "CLAS 104": ("Classical Mythology", "CLAS", "Themes and narratives from classical antiquity."),
    "HRM 200": ("Basic Human Resources Management", "HRM", "Workplace management and HR foundations."),
    "REC 100": ("Introduction to Recreation and Leisure Studies", "REC", "Foundations of recreation studies."),
    "ENVS 200": ("Field Ecology", "ENVS", "Ecological systems and field methods."),
    "SOC 101": ("Introduction to Sociology", "SOC", "Social structures and institutions."),
    "PSCI 150": ("Politics and the State", "PSCI", "Political systems and governance."),
    "MSCI 211": ("Organizational Behaviour", "MSCI", "Team dynamics and organizational design."),
    "ENBUS 102": ("Introduction to Sustainable Entrepreneurship", "ENBUS", "Entrepreneurship with a sustainability lens."),
    "BET 210": ("Principles of Entrepreneurial Finance", "BET", "Finance basics for startup contexts."),
    "LS 283": ("The Charter of Rights and Freedoms", "LS", "Canadian constitutional rights overview."),
    "MUSIC 140": ("Understanding Music", "MUSIC", "Introductory music literacy and appreciation."),
}


def _course(code: str) -> CourseDefinition:
    title, subject, description = COURSE_CATALOG[code]
    return CourseDefinition(code=code, title=title, subject=subject, description=description, credits=0.5)


def _course_requirement(
    course_code: str,
    sequence: int,
    *,
    prerequisites: list[str] | None = None,
    notes: str | None = None,
) -> CourseRequirementDefinition:
    return CourseRequirementDefinition(
        code=course_code.replace(" ", "_"),
        course=_course(course_code),
        sequence=sequence,
        notes=notes,
        prerequisites=[PrerequisiteDefinition(course_code=code) for code in prerequisites or []],
    )


def _group_option(
    course_code: str,
    sequence: int,
    *,
    prerequisites: list[str] | None = None,
    notes: str | None = None,
) -> CourseRequirementDefinition:
    return CourseRequirementDefinition(
        code=f"OPTION_{course_code.replace(' ', '_')}",
        course=_course(course_code),
        sequence=sequence,
        notes=notes,
        prerequisites=[PrerequisiteDefinition(course_code=code) for code in prerequisites or []],
        kind=RequirementKind.ELECTIVE_GROUP,
    )


def _group(
    code: str,
    title: str,
    description: str,
    sequence: int,
    options: list[str],
) -> ElectiveGroupDefinition:
    return ElectiveGroupDefinition(
        code=code,
        title=title,
        description=description,
        kind=RequirementGroupKind.ONE_OF,
        min_selections=1,
        max_selections=1,
        sequence=sequence,
        options=[_group_option(course_code, option_index + 1) for option_index, course_code in enumerate(options)],
    )


def build_computer_science_program_definition() -> ProgramDefinition:
    return ProgramDefinition(
        university_code="WATERLOO",
        program_code="CS",
        name="Computer Science",
        degree="Bachelor of Computer Science",
        description="A production-style sample roadmap for Waterloo Computer Science with core courses, electives, and prerequisites.",
        terms=[
            TermDefinition(
                code="Y1_FALL",
                label="Year 1 Fall",
                year=1,
                season=TermSeason.FALL,
                sequence=1,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 135", 1)),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=2, course=_course_requirement("MATH 135", 2)),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=3, course=_course_requirement("MATH 137", 3)),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=4, course=_course_requirement("COMMST 100", 4)),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=5,
                        group=_group(
                            "Y1_FALL_BREADTH",
                            "Choose 1 breadth elective",
                            "Pick one humanities or social science course to round out the first term.",
                            5,
                            ["ECON 101", "PSYCH 101", "ENGL 109"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y1_WINTER",
                label="Year 1 Winter",
                year=1,
                season=TermSeason.WINTER,
                sequence=2,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 136", 1, prerequisites=["CS 135"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=2, course=_course_requirement("MATH 136", 2, prerequisites=["MATH 135"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=3, course=_course_requirement("MATH 138", 3, prerequisites=["MATH 137"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=4, course=_course_requirement("STAT 230", 4, prerequisites=["MATH 137"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=5,
                        group=_group(
                            "Y1_WINTER_SCIENCE",
                            "Choose 1 science elective",
                            "A lab-friendly science pick keeps the plan broad in first year.",
                            5,
                            ["BIOL 130", "CHEM 120", "PHYS 121"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y1_SPRING",
                label="Year 1 Spring",
                year=1,
                season=TermSeason.SPRING,
                sequence=3,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 245", 1, prerequisites=["CS 136"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=2, course=_course_requirement("CS 246", 2, prerequisites=["CS 136"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=3, course=_course_requirement("MATH 239", 3, prerequisites=["MATH 136"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=4,
                        group=_group(
                            "Y1_SPRING_COMM",
                            "Choose 1 communication elective",
                            "Waterloo CS students often complement core theory with communication-focused work.",
                            4,
                            ["SPCOM 100", "ENGL 210F", "LS 101"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y2_FALL",
                label="Year 2 Fall",
                year=2,
                season=TermSeason.FALL,
                sequence=4,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 240", 1, prerequisites=["CS 136"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=2, course=_course_requirement("CS 241", 2, prerequisites=["CS 136"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=3, course=_course_requirement("STAT 231", 3, prerequisites=["STAT 230"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=4,
                        group=_group(
                            "Y2_FALL_BUSINESS",
                            "Choose 1 context elective",
                            "A business or history course helps frame product and systems work.",
                            4,
                            ["AFM 101", "BET 100", "HIST 101"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y2_WINTER",
                label="Year 2 Winter",
                year=2,
                season=TermSeason.WINTER,
                sequence=5,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 251", 1, prerequisites=["CS 245"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=2, course=_course_requirement("CS 341", 2, prerequisites=["CS 240"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=3, course=_course_requirement("CS 350", 3, prerequisites=["CS 246"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=4,
                        group=_group(
                            "Y2_WINTER_HUMANITIES",
                            "Choose 1 humanities elective",
                            "Pick one humanities elective to satisfy a broader degree requirement.",
                            4,
                            ["PHIL 145", "CLAS 104", "HRM 200"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y2_SPRING",
                label="Year 2 Spring",
                year=2,
                season=TermSeason.SPRING,
                sequence=6,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 348", 1, prerequisites=["CS 246"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=2, course=_course_requirement("CS 349", 2, prerequisites=["CS 246"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=3,
                        group=_group(
                            "Y2_SPRING_CS_ELECTIVE",
                            "Choose 1 applied CS elective",
                            "An early CS elective lets the student lean toward systems, theory, or applications.",
                            3,
                            ["CS 338", "CS 346", "CS 360"],
                        ),
                    ),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=4,
                        group=_group(
                            "Y2_SPRING_FREE",
                            "Choose 1 free elective",
                            "A free elective keeps the MVP roadmap realistic without over-constraining specialization.",
                            4,
                            ["ECON 201", "PSYCH 207", "REC 100"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y3_FALL",
                label="Year 3 Fall",
                year=3,
                season=TermSeason.FALL,
                sequence=7,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 370", 1, prerequisites=["CS 245", "STAT 230"])),
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=2, course=_course_requirement("CS 371", 2, prerequisites=["CS 241"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=3,
                        group=_group(
                            "Y3_FALL_UPPER_CS",
                            "Choose 1 upper-year CS elective",
                            "Select an upper-year CS area of interest.",
                            3,
                            ["CS 454", "CS 458", "CS 475"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y3_WINTER",
                label="Year 3 Winter",
                year=3,
                season=TermSeason.WINTER,
                sequence=8,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 486", 1, prerequisites=["CS 370"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=2,
                        group=_group(
                            "Y3_WINTER_SOCIETY",
                            "Choose 1 society elective",
                            "A non-technical elective rounds out upper-year planning.",
                            2,
                            ["ENVS 200", "SOC 101", "PSCI 150"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y4_FALL",
                label="Year 4 Fall",
                year=4,
                season=TermSeason.FALL,
                sequence=9,
                requirements=[
                    TermRequirementDefinition(kind=RequirementKind.COURSE, sequence=1, course=_course_requirement("CS 445", 1, prerequisites=["CS 341"])),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=2,
                        group=_group(
                            "Y4_FALL_SYSTEMS",
                            "Choose 1 advanced systems elective",
                            "Use fourth year to deepen a technical specialization.",
                            2,
                            ["CS 444", "CS 452", "CS 479"],
                        ),
                    ),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=3,
                        group=_group(
                            "Y4_FALL_PRODUCT",
                            "Choose 1 product or entrepreneurship elective",
                            "This slot supports product, entrepreneurship, or management interests.",
                            3,
                            ["MSCI 211", "ENBUS 102", "BET 210"],
                        ),
                    ),
                ],
            ),
            TermDefinition(
                code="Y4_WINTER",
                label="Year 4 Winter",
                year=4,
                season=TermSeason.WINTER,
                sequence=10,
                requirements=[
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=1,
                        group=_group(
                            "Y4_WINTER_CAPSTONE",
                            "Choose 1 capstone or synthesis course",
                            "Wrap the degree with a capstone-style or synthesis-oriented course.",
                            1,
                            ["CS 490", "CS 492", "CS 497"],
                        ),
                    ),
                    TermRequirementDefinition(
                        kind=RequirementKind.ELECTIVE_GROUP,
                        sequence=2,
                        group=_group(
                            "Y4_WINTER_FREE",
                            "Choose 1 final elective",
                            "Leave one slot for a final area of curiosity or breadth.",
                            2,
                            ["ECON 290", "LS 283", "MUSIC 140"],
                        ),
                    ),
                ],
            ),
        ],
    )
