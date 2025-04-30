# app/core/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database # Use this OR SQLAlchemy async below

# Get DB URL from environment variable (best practice)
# Ensure this matches the DATABASE_URL in your k8s-secrets.yaml (decoded)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://qna_user:supersecret@postgres-service:5432/qna_db")

# --- Option 1: Using 'databases' library ---
database = Database(DATABASE_URL)

async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()
# -----------------------------------------

# --- Option 2: Using SQLAlchemy async setup ---
# engine = create_async_engine(DATABASE_URL, echo=False) # Set echo=True for SQL debugging
# Base = declarative_base()
# AsyncSessionLocal = sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )
#
# async def get_db():
#     async with AsyncSessionLocal() as session:
#         yield session
#
# # If using SQLAlchemy, you don't typically need global connect/disconnect
# # The session context manager handles connections per request via Depends(get_db)
#
# # Make Base accessible for models.py
# def get_base():
#     return Base
# -----------------------------------------

# If using Option 1 ('databases'), add connect/disconnect to FastAPI startup/shutdown
# If using Option 2 (SQLAlchemy), you'll use Depends(get_db) in endpoints
