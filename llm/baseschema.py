from pydantic import BaseModel, ConfigDict


class QueryStructures(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: list[str]


# print(QueryStructures.model_json_schema())
