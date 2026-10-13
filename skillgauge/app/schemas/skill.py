from pydantic import BaseModel, Field


class SkillRead(BaseModel):
    id: int
    name: str
    description: str
    category: str

    model_config = {"from_attributes": True}
