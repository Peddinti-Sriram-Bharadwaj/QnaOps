from fastapi import APIRouter, Depends
from app.models.schemas import QARequest, QAResponse
from app.services.qna_engine import get_answer

router = APIRouter()

@router.post("/answer/", response_model = QAResponse)
def answer_query(request: QARequest):
    answer = get_answer(
        context = request.context, 
        question = request.question, 
        model_version = request.model_version
    )
    return {"answer": answer}