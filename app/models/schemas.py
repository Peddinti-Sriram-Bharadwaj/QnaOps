from pydantic import BaseModel

class QARequest(BaseModel):
    context: str
    question: str
    model_version: str = "v1"

class QAResponse(BaseModel):
    answer: str