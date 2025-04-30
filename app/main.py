# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # For serving UI
from app.api import v1 as api_v1 # Import the v1 router
from app.core.database import connect_db, disconnect_db # If using 'databases' library

app = FastAPI(title="QnA Bot")

# --- Add startup/shutdown events (ONLY if using 'databases' library) ---
@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()
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
