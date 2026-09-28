from pydantic import BaseModel, Field


class UserInput(BaseModel):
    username: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    age: int = Field(..., gt=0, lt=120)
    weight: float = Field(..., gt=0)
    goal: str = Field(..., min_length=1)
    intensity: str = Field(..., min_length=1)


class FeedbackRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    feedback: str = Field(..., min_length=1)
