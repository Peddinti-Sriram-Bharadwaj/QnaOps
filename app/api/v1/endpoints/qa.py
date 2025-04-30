# app/api/v1/endpoints/qa.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.crud import qa_crud as crud # Renamed import for clarity
from app.models import schemas
# from sqlalchemy.ext.asyncio import AsyncSession # Uncomment if using SQLAlchemy sessions
# from app.core.database import get_db # Uncomment if using SQLAlchemy sessions

router = APIRouter()

# --- Your Existing QnA Logic (Modified) ---
@router.post("/ask", response_model=schemas.AnswerOutput)
async def ask_question(
    payload: schemas.QuestionInput,
    # db: AsyncSession = Depends(get_db) # Uncomment if using SQLAlchemy sessions
):
    """
    Receives a question, gets an answer (placeholder/model),
    stores it, and returns answer with QA ID.
    """
    question = payload.question
    # --- Placeholder for getting the actual answer ---
    # answer = await get_answer_from_model(question) # Replace with your model call
    answer = f"This is a placeholder answer for '{question}'."
    # -------------------------------------------------

    if not answer:
         raise HTTPException(status_code=404, detail="Could not generate an answer.")

    try:
        # Pass db session if using SQLAlchemy CRUD functions
        qa_id = await crud.create_qa_entry(question=question, answer=answer)
        return schemas.AnswerOutput(qa_id=qa_id, question=question, answer=answer)
    except Exception as e:
        # Add proper logging here
        print(f"Error saving Q&A: {e}") # Replace with logger
        raise HTTPException(status_code=500, detail="Failed to store Q&A pair.")

# --- New Endpoints ---

@router.post("/feedback/{qa_id}", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    qa_id: str,
    feedback: schemas.FeedbackInput,
    # db: AsyncSession = Depends(get_db) # Uncomment if using SQLAlchemy sessions
):
    """Submits feedback for a given Q&A ID."""
    qa = await crud.get_qa_by_id(qa_id) # Pass db if needed
    if not qa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Q&A not found.")

    allowed_ratings = {"helpful", "unhelpful"}
    if feedback.rating not in allowed_ratings:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rating value.")

    try:
        await crud.add_feedback(qa_id=qa_id, rating=feedback.rating) # Pass db if needed
        return {"message": "Feedback submitted successfully."}
    except Exception as e:
        # Add proper logging here
        print(f"Error submitting feedback: {e}") # Replace with logger
        raise HTTPException(status_code=500, detail="Failed to store feedback.")

@router.get("/qa/{qa_id}", response_model=schemas.QAOutput)
async def get_shared_qa(
    qa_id: str,
    # db: AsyncSession = Depends(get_db) # Uncomment if using SQLAlchemy sessions
):
    """Retrieves a specific Q&A pair for sharing."""
    qa = await crud.get_qa_by_id(qa_id) # Pass db if needed
    if not qa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Q&A not found.")

    try:
        await crud.increment_qa_view_count(qa_id) # Pass db if needed
    except Exception as e:
        # Log this error but don't fail the request just because view count failed
        print(f"Error incrementing view count for {qa_id}: {e}") # Replace with logger

    # Convert the dictionary-like result from crud to the Pydantic model
    # Ensure keys match Pydantic field names
    return schemas.QAOutput(**qa)

@router.get("/popular-questions", response_model=List[schemas.PopularQuestion])
async def list_popular_questions(
    limit: int = 5,
    # db: AsyncSession = Depends(get_db) # Uncomment if using SQLAlchemy sessions
):
    """Gets the most popular (most viewed) questions."""
    try:
        popular = await crud.get_popular_questions(limit=limit) # Pass db if needed
        # Convert list of dict-like results to list of Pydantic models
        return [schemas.PopularQuestion(**q) for q in popular]
    except Exception as e:
         # Add proper logging here
        print(f"Error getting popular questions: {e}") # Replace with logger
        raise HTTPException(status_code=500, detail="Failed to retrieve popular questions.")
