from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.config import get_settings
from app.graphql.context import get_graphql_context
from app.graphql.schema import graphql_schema


settings = get_settings()


def create_application() -> FastAPI:
    app = FastAPI(
        title="PlanAhead Backend",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    graphql_app = GraphQLRouter(
        schema=graphql_schema,
        context_getter=get_graphql_context,
    )

    @app.get("/health", tags=["system"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {"message": "PlanAhead backend is running.", "graphql": settings.graphql_path}

    app.include_router(graphql_app, prefix=settings.graphql_path)
    return app


app = create_application()
