"""Initial schema for PlanAhead MVP.

Revision ID: 20260412_0001
Revises:
Create Date: 2026-04-12 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260412_0001"
down_revision = None
branch_labels = None
depends_on = None


course_status_enum = sa.Enum("NOT_STARTED", "PLANNED", "IN_PROGRESS", "COMPLETED", name="coursestatus", native_enum=False)
requirement_kind_enum = sa.Enum("COURSE", "ELECTIVE_GROUP", name="requirementkind", native_enum=False)
requirement_group_kind_enum = sa.Enum("CORE", "ELECTIVE", "ONE_OF", name="requirementgroupkind", native_enum=False)
term_season_enum = sa.Enum("FALL", "WINTER", "SPRING", name="termseason", native_enum=False)


def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("external_key", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("external_key"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_students_external_key"), "students", ["external_key"], unique=False)

    op.create_table(
        "universities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_universities_code"), "universities", ["code"], unique=False)

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("university_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=64), nullable=False),
        sa.Column("credits", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("university_id", "code", name="uq_course_university_code"),
    )
    op.create_index(op.f("ix_courses_code"), "courses", ["code"], unique=False)
    op.create_index(op.f("ix_courses_university_id"), "courses", ["university_id"], unique=False)

    op.create_table(
        "programs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("university_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("degree", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("university_id", "code", name="uq_program_university_code"),
    )
    op.create_index(op.f("ix_programs_code"), "programs", ["code"], unique=False)
    op.create_index(op.f("ix_programs_university_id"), "programs", ["university_id"], unique=False)

    op.create_table(
        "program_plan_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("program_id"),
    )
    op.create_index(op.f("ix_program_plan_templates_program_id"), "program_plan_templates", ["program_id"], unique=False)

    op.create_table(
        "terms",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("program_plan_template_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("season", term_season_enum, nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["program_plan_template_id"], ["program_plan_templates.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("program_plan_template_id", "code", name="uq_term_template_code"),
    )
    op.create_index(op.f("ix_terms_code"), "terms", ["code"], unique=False)
    op.create_index(op.f("ix_terms_program_plan_template_id"), "terms", ["program_plan_template_id"], unique=False)
    op.create_index(op.f("ix_terms_sequence"), "terms", ["sequence"], unique=False)

    op.create_table(
        "prerequisite_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("prerequisite_course_id", sa.Integer(), nullable=False),
        sa.Column("minimum_grade", sa.String(length=16), nullable=True),
        sa.Column("is_corequisite", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["prerequisite_course_id"], ["courses.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_prerequisite_rules_course_id"), "prerequisite_rules", ["course_id"], unique=False)
    op.create_index(op.f("ix_prerequisite_rules_prerequisite_course_id"), "prerequisite_rules", ["prerequisite_course_id"], unique=False)

    op.create_table(
        "requirement_groups",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("term_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("kind", requirement_group_kind_enum, nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("min_selections", sa.Integer(), nullable=False),
        sa.Column("max_selections", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["term_id"], ["terms.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_requirement_groups_code"), "requirement_groups", ["code"], unique=False)
    op.create_index(op.f("ix_requirement_groups_program_id"), "requirement_groups", ["program_id"], unique=False)
    op.create_index(op.f("ix_requirement_groups_sequence"), "requirement_groups", ["sequence"], unique=False)
    op.create_index(op.f("ix_requirement_groups_term_id"), "requirement_groups", ["term_id"], unique=False)

    op.create_table(
        "elective_groups",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("requirement_group_id", sa.Integer(), nullable=False),
        sa.Column("selection_label", sa.String(length=255), nullable=False),
        sa.Column("credits_required", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["requirement_group_id"], ["requirement_groups.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("requirement_group_id"),
    )
    op.create_index(op.f("ix_elective_groups_requirement_group_id"), "elective_groups", ["requirement_group_id"], unique=False)

    op.create_table(
        "program_requirements",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("term_id", sa.Integer(), nullable=False),
        sa.Column("requirement_group_id", sa.Integer(), nullable=True),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("requirement_type", requirement_kind_enum, nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("display_title", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_recommended", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requirement_group_id"], ["requirement_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["term_id"], ["terms.id"], ondelete="CASCADE"),
    )
    op.create_index(op.f("ix_program_requirements_course_id"), "program_requirements", ["course_id"], unique=False)
    op.create_index(op.f("ix_program_requirements_program_id"), "program_requirements", ["program_id"], unique=False)
    op.create_index(op.f("ix_program_requirements_requirement_group_id"), "program_requirements", ["requirement_group_id"], unique=False)
    op.create_index(op.f("ix_program_requirements_sequence"), "program_requirements", ["sequence"], unique=False)
    op.create_index(op.f("ix_program_requirements_term_id"), "program_requirements", ["term_id"], unique=False)

    op.create_table(
        "student_course_progress",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("status", course_status_enum, nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("student_id", "program_id", "course_id", name="uq_student_program_course_progress"),
    )
    op.create_index(op.f("ix_student_course_progress_course_id"), "student_course_progress", ["course_id"], unique=False)
    op.create_index(op.f("ix_student_course_progress_program_id"), "student_course_progress", ["program_id"], unique=False)
    op.create_index(op.f("ix_student_course_progress_student_id"), "student_course_progress", ["student_id"], unique=False)

    op.create_table(
        "elective_selections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("program_id", sa.Integer(), nullable=False),
        sa.Column("elective_group_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["elective_group_id"], ["elective_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("student_id", "program_id", "elective_group_id", name="uq_student_program_elective"),
    )
    op.create_index(op.f("ix_elective_selections_course_id"), "elective_selections", ["course_id"], unique=False)
    op.create_index(op.f("ix_elective_selections_elective_group_id"), "elective_selections", ["elective_group_id"], unique=False)
    op.create_index(op.f("ix_elective_selections_program_id"), "elective_selections", ["program_id"], unique=False)
    op.create_index(op.f("ix_elective_selections_student_id"), "elective_selections", ["student_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_elective_selections_student_id"), table_name="elective_selections")
    op.drop_index(op.f("ix_elective_selections_program_id"), table_name="elective_selections")
    op.drop_index(op.f("ix_elective_selections_elective_group_id"), table_name="elective_selections")
    op.drop_index(op.f("ix_elective_selections_course_id"), table_name="elective_selections")
    op.drop_table("elective_selections")

    op.drop_index(op.f("ix_student_course_progress_student_id"), table_name="student_course_progress")
    op.drop_index(op.f("ix_student_course_progress_program_id"), table_name="student_course_progress")
    op.drop_index(op.f("ix_student_course_progress_course_id"), table_name="student_course_progress")
    op.drop_table("student_course_progress")

    op.drop_index(op.f("ix_program_requirements_term_id"), table_name="program_requirements")
    op.drop_index(op.f("ix_program_requirements_sequence"), table_name="program_requirements")
    op.drop_index(op.f("ix_program_requirements_requirement_group_id"), table_name="program_requirements")
    op.drop_index(op.f("ix_program_requirements_program_id"), table_name="program_requirements")
    op.drop_index(op.f("ix_program_requirements_course_id"), table_name="program_requirements")
    op.drop_table("program_requirements")

    op.drop_index(op.f("ix_elective_groups_requirement_group_id"), table_name="elective_groups")
    op.drop_table("elective_groups")

    op.drop_index(op.f("ix_requirement_groups_term_id"), table_name="requirement_groups")
    op.drop_index(op.f("ix_requirement_groups_sequence"), table_name="requirement_groups")
    op.drop_index(op.f("ix_requirement_groups_program_id"), table_name="requirement_groups")
    op.drop_index(op.f("ix_requirement_groups_code"), table_name="requirement_groups")
    op.drop_table("requirement_groups")

    op.drop_index(op.f("ix_prerequisite_rules_prerequisite_course_id"), table_name="prerequisite_rules")
    op.drop_index(op.f("ix_prerequisite_rules_course_id"), table_name="prerequisite_rules")
    op.drop_table("prerequisite_rules")

    op.drop_index(op.f("ix_terms_sequence"), table_name="terms")
    op.drop_index(op.f("ix_terms_program_plan_template_id"), table_name="terms")
    op.drop_index(op.f("ix_terms_code"), table_name="terms")
    op.drop_table("terms")

    op.drop_index(op.f("ix_program_plan_templates_program_id"), table_name="program_plan_templates")
    op.drop_table("program_plan_templates")

    op.drop_index(op.f("ix_programs_university_id"), table_name="programs")
    op.drop_index(op.f("ix_programs_code"), table_name="programs")
    op.drop_table("programs")

    op.drop_index(op.f("ix_courses_university_id"), table_name="courses")
    op.drop_index(op.f("ix_courses_code"), table_name="courses")
    op.drop_table("courses")

    op.drop_index(op.f("ix_universities_code"), table_name="universities")
    op.drop_table("universities")

    op.drop_index(op.f("ix_students_external_key"), table_name="students")
    op.drop_table("students")
