from pydantic import BaseModel, ConfigDict

class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunk_id: int
    quote:str
class AnswerStructure(BaseModel):
    model_config = ConfigDict(extra="forbid")
    citations: list[Citation]
    answer: str
