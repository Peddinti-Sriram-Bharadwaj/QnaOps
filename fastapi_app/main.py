import psycopg2
import redis
import os
import logging
import sys
import json_log_formatter
import requests

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
ASHUTOSH_SERVER_IP = os.environ.get("ASHUTOSH_SERVER_IP", "https://60ee-49-207-60-154.ngrok-free.app/answer")  # endpoint that handles question answering

r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASSWORD, decode_responses=True)

conn = psycopg2.connect(
    dbname="postgres",
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST
)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
        context TEXT,
        question TEXT
    )
""")
conn.commit()

formatter = json_log_formatter.JSONFormatter()
json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(formatter)

logger = logging.getLogger("uvicorn.access")
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)

templates = Jinja2Templates(directory="templates")
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    recent = r.lrange("recent_questions", 0, 4)
    questions = [{"question": q.split("::")[0], "context": q.split("::")[1]} for q in recent]
    return templates.TemplateResponse("index.html", {"request": request, "questions": questions})

@app.post("/submit", response_class=HTMLResponse)
async def submit_question(request: Request, context: str = Form(...), question: str = Form(...)):
    # Log and DB store
    r.lpush("recent_questions", f"{question}::{context}")
    cursor.execute("INSERT INTO questions (context, question) VALUES (%s, %s)", (context, question))
    conn.commit()

    # Send to remote server
    try:
        response = requests.post(ASHUTOSH_SERVER_IP, json={"question": question, "context": context}, timeout=5)
        response.raise_for_status()
        answer = response.json().get("answer", "[No answer received]")
    except Exception as e:
        logger.error(f"Failed to fetch answer: {e}")
        answer = "[Error getting answer]"

    # Build question list with answer
    recent = r.lrange("recent_questions", 0, 4)
    questions = [{"question": q.split("::")[0], "context": q.split("::")[1]} for q in recent]


    return templates.TemplateResponse("index.html", {
    "request": request,
    "questions": questions,
    "answer": answer
})

