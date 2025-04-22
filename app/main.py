from fastapi import FastAPI
from app.api import v1

app = FastAPI(title = "QnA Bot")


app.include_router(v1.router, prefix = "/api/v1")