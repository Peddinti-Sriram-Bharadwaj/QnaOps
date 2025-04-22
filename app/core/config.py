import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    REDIS_HOST = os.getenv("REDIS_HOST")
    POSTGRES_USER = os.getenv("POSTGRES_USER")

settings = Settings()