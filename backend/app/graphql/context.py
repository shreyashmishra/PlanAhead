from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.repositories.student_repository import StudentRepository
from app.db.session import get_db_session
from app.modules.programs.service import ProgramCatalogService
from app.modules.students.service import StudentProgressService


@dataclass
class GraphQLContext:
    db: Session
    programs: ProgramCatalogService
    students: StudentProgressService


def get_graphql_context(db: Session = Depends(get_db_session)) -> GraphQLContext:
    return GraphQLContext(
        db=db,
        programs=ProgramCatalogService(db),
        students=StudentProgressService(db),
    )


DEFAULT_STUDENT_KEY = StudentRepository.DEMO_STUDENT_KEY
