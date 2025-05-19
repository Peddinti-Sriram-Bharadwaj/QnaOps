# app/main.py
import logging # For logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # For serving UI
from app.api import v1 as api_v1 # Import the v1 router
from app.core.database import connect_db, disconnect_db, create_db_tables # Import create_db_tables
from app.models import models # IMPORTANT: Import your models module so Base knows about them
from app.api import qa

app = FastAPI(title="QnA Bot")

app.include_router(qa.router, prefix="/qa/v1", tags=["Q&A System"])

# --- Add startup/shutdown events (ONLY if using 'databases' library) ---
# We'll also add table creation here.
@app.on_event("startup")
async def startup_event():
    logger = logging.getLogger(__name__)
    logger.info("Application starting up...")
    await connect_db()
    logger.info("Database connection established via 'databases' lib.")
    await create_db_tables() # Create database tables defined by SQLAlchemy models
    logger.info("Database tables checked/created via SQLAlchemy.")

@app.on_event("shutdown")
async def shutdown_event():
    logger = logging.getLogger(__name__)
    await disconnect_db()
    logger.info("Database connection closed via 'databases' lib.")
# ---------------------------------------------------------------------

# Include the API router with a prefix
app.include_router(api_v1.router, prefix="/api/v1")

# --- Mount static files (Optional: If FastAPI serves the UI) ---
# Create a 'static' directory at the project root for index.html, script.js
app.mount("/static", StaticFiles(directory="static"), name="static")

# Optional: Serve index.html at the root path
from fastapi.responses import FileResponse
@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse('static/index.html')
# -------------------------------------------------------------

# Add the health check endpoint directly here or ensure it's in a router
@app.get("/health", status_code=200, tags=["Health"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

# Add other global middleware, exception handlers etc. if needed
