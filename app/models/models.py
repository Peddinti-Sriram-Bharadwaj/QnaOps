# app/models/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func
# from sqlalchemy.dialects.postgresql import UUID # Alternative ID type
import ulid
from app.core.database import Base # Assuming SQLAlchemy setup from database.py

class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id = Column(String, primary_key=True, default=lambda: str(ulid.new()))
    question = Column(Text, nullable=False, index=True)
    answer = Column(Text, nullable=True)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Add other fields like model_version used, etc. if needed

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True) # Simple auto-incrementing ID
    qa_id = Column(String, index=True, nullable=False) # Corresponds to QuestionAnswer.id
    rating = Column(String, nullable=False) # e.g., 'helpful', 'unhelpful'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
