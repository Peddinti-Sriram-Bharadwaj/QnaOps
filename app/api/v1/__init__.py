# app/api/v1/__init__.py
from fastapi import APIRouter
from .endpoints import qa # Import your new endpoint module

# You might have other endpoint modules here too
# from .endpoints import other_endpoint

api_router = APIRouter()
api_router.include_router(qa.router, prefix="/qna", tags=["QnA & Feedback"]) # Added prefix
# api_router.include_router(other_endpoint.router, prefix="/other", tags=["Other"])

# Export the main router for this version
router = api_router
