from pydantic import BaseModel
from typing import Optional, List
import datetime

class QARequest(BaseModel):
    context: str
    question: str
    model_version: str = "v1"

class QAResponse(BaseModel):
    answer: str

# Input for asking a question
class QuestionInput(BaseModel):
    question: str

# Output when asking a question
class AnswerOutput(BaseModel):
    qa_id: str # Unique ID for this Q&A pair
    question: str
    answer: str

# Input for submitting feedback
class FeedbackInput(BaseModel):
    rating: str # e.g., "helpful" or "unhelpful"

# Output for a single Q&A pair (for sharing)
class QAOutput(BaseModel):
    id: str
    question: str
    answer: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True # Enable ORM mode if using SQLAlchemy models

# Output for popular questions list
class PopularQuestion(BaseModel):
    id: str
    question: str
    view_count: int

    class Config:
        orm_mode = True # Enable ORM mode if using SQLAlchemy models