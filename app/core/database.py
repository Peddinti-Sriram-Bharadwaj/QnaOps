# app/core/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database # Use this OR SQLAlchemy async below

# Get DB URL from environment variable (best practice)
# Ensure this matches the DATABASE_URL in your k8s-secrets.yaml (decoded)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://qna_user:supersecret@postgres-service:5432/qna_db")

# --- Option 1: Using 'databases' library (Can be kept for other uses or removed if fully switching to SQLAlchemy ORM) ---
database = Database(DATABASE_URL)

async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()
# -----------------------------------------

# --- Option 2: Using SQLAlchemy async setup ---
engine = create_async_engine(DATABASE_URL, echo=True) # Set echo=True for SQL debugging during development. Note: DATABASE_URL for 'databases' lib doesn't need +asyncpg, but SQLAlchemy async engine does.
Base = declarative_base() # This Base is imported by your models.py
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Function to create database tables
async def create_db_tables():
    """Creates database tables if they don't exist, based on SQLAlchemy models."""
    # Ensure DATABASE_URL is correctly formed for async operations
    print(f"DEBUG: DATABASE_URL used for engine creation: {DATABASE_URL}")
    async with engine.begin() as conn:
        # In an async context, run_sync is used for create_all
        # Make sure all your models that use Base are imported before this runs.
        # This is usually handled if app.models.models imports Base from here.
        await conn.run_sync(Base.metadata.create_all)
    # Consider using a proper logger here instead of print
    print(f"Database tables checked/created for engine: {engine.url}")

# -----------------------------------------

# If using Option 1 ('databases'), add connect/disconnect to FastAPI startup/shutdown
# If using Option 2 (SQLAlchemy), you'll use Depends(get_db) in endpoints
