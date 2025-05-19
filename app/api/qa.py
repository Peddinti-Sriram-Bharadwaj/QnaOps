from fastapi import APIRouter
from app.models.schemas import QARequest, QAResponse  # Assuming these are defined
from app.services.qna_engine import get_answer      # Assuming this is your service

router = APIRouter()

@router.post("/ask/", response_model=QAResponse)
async def process_question_answer(request: QARequest):
    """
    Receives a question and context, and returns an answer using the QnA engine.
    """
    answer_text = get_answer(
        context=request.context,
        question=request.question,
        model_version=request.model_version
    )
    return QAResponse(answer=answer_text)