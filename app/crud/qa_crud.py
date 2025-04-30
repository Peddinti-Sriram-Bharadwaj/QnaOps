# app/crud/qa_crud.py
from app.core.database import database # Assuming 'databases' setup
import ulid
from typing import List, Dict, Any, Optional
# from app.models import models # Import only needed if using SQLAlchemy types

async def create_qa_entry(question: str, answer: str) -> str:
    """Creates a new Q&A entry and returns its ID."""
    qa_id = str(ulid.ULID())
    query = """
        INSERT INTO question_answers(id, question, answer, view_count, created_at)
        VALUES(:id, :question, :answer, :view_count, NOW())
        RETURNING id
    """
    values = {
        "id": qa_id,
        "question": question,
        "answer": answer,
        "view_count": 1 # Start view count at 1
    }
    result = await database.fetch_one(query=query, values=values)
    if result:
        return result["id"]
    raise Exception("Failed to create Q&A entry") # Or more specific error

async def get_qa_by_id(qa_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a specific Q&A pair by ID."""
    query = "SELECT id, question, answer, created_at FROM question_answers WHERE id = :id"
    result = await database.fetch_one(query=query, values={"id": qa_id})
    return result # Returns a dictionary-like object or None

async def increment_qa_view_count(qa_id: str):
    """Increments the view count for a given Q&A ID."""
    query = """
        UPDATE question_answers
        SET view_count = view_count + 1
        WHERE id = :id
    """
    await database.execute(query=query, values={"id": qa_id})

async def add_feedback(qa_id: str, rating: str):
    """Adds feedback for a specific Q&A pair."""
    query = """
        INSERT INTO feedback(qa_id, rating, created_at)
        VALUES(:qa_id, :rating, NOW())
    """
    await database.execute(query=query, values={"qa_id": qa_id, "rating": rating})

async def get_popular_questions(limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieves the most viewed questions."""
    query = """
        SELECT id, question, view_count
        FROM question_answers
        ORDER BY view_count DESC
        LIMIT :limit
    """
    results = await database.fetch_all(query=query, values={"limit": limit})
    return results
