from __future__ import annotations

import strawberry
from strawberry.schema.config import StrawberryConfig

from app.graphql.mutations.mutation import Mutation
from app.graphql.queries.query import Query


graphql_schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    config=StrawberryConfig(auto_camel_case=True),
)
