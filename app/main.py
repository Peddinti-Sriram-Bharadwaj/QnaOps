# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

# Assuming qa_service.py is in app/services/
from app.services.qa_service import get_answer, question_answerer_pipeline

app = FastAPI(
    title="Q&A FastAPI Application",
    description="Provides an API for question answering using a Hugging Face transformer model.",
    version="1.0.0"
)

logger = logging.getLogger(__name__)

class QARequest(BaseModel):
    context: str
    question: str

class QAResponse(BaseModel):
    answer: str | None
    score: float | None
    start: int | None
    end: int | None
    error: str | None = None

@app.on_event("startup")
async def startup_event():
    if question_answerer_pipeline is None:
        logger.critical("CRITICAL: Question answering model could not be loaded. The /api/v1/qna/ask endpoint will not function correctly.")
    else:
        logger.info("Question answering model loaded successfully. The /api/v1/qna/ask endpoint is ready.")

@app.post("/api/v1/qna/ask", response_model=QAResponse, tags=["Q&A"])
async def ask_qna(request: QARequest):
    """
    Accepts a context and a question, returns an answer from the context.
    """
    if question_answerer_pipeline is None:
        logger.warning("Attempt to use /api/v1/qna/ask endpoint, but model is not loaded.")
        raise HTTPException(status_code=503, detail="Model not available. Please try again later.")

    if not request.context or not request.question:
        raise HTTPException(status_code=400, detail="Both 'context' and 'question' must be provided.")

    result = get_answer(question=request.question, context=request.context)

    if result.get("error"):
        logger.error(f"Error processing Q&A request: {result.get('error')}")
        # Return a 500 error if the service layer indicated an issue
        raise HTTPException(status_code=500, detail=result.get("error"))

    return QAResponse(
        answer=result.get("answer"),
        score=result.get("score"),
        start=result.get("start"),
        end=result.get("end")
    )

# Your existing /health endpoint (from k8s-fastapi.yaml readiness/liveness probes)
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    """
    if question_answerer_pipeline is None:
        return {"status": "unhealthy", "reason": "QA model not loaded"}
    return {"status": "healthy"}

# If you want to run this file directly with uvicorn for local testing:
# (Ensure your MODEL_DIR points to a valid model locally for this to work,
# or the fallback in qa_service.py is active and downloads the model)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
