from fastapi import APIRouter, Depends

router = APIRouter()

# This file can be used to aggregate other v1 routers if needed,
# or can be removed if all v1 endpoints are within specific modules like qa.py.
# For now, we'll leave it minimal.