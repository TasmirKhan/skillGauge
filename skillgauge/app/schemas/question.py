from pydantic import BaseModel, Field


class QuestionRead(BaseModel):
    id: int
    skill_id: int
    question_text: str
    options: list[str] = Field(..., min_length=4, max_length=4)
    difficulty: str
    topic: str

    model_config = {"from_attributes": True}
