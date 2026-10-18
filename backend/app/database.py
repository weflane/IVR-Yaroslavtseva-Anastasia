import os

import certifi
from dotenv import load_dotenv
from mongoengine import connect

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB_NAME", "bookmatch")


def init_db():
    """Подключение к MongoDB. Если база недоступна, сервер сразу скажет об этом при запуске."""
    extra = {}
    if MONGODB_URL.startswith("mongodb+srv://") or "mongodb.net" in MONGODB_URL:
        extra["tlsCAFile"] = certifi.where()
    try:
        client = connect(
            db=MONGODB_DB,
            host=MONGODB_URL,
            alias="default",
            serverSelectionTimeoutMS=8000,
            **extra,
        )
        client.admin.command("ping")
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Проверь MONGODB_URL, логин и пароль базы и доступ по IP в Atlas (Network Access).")
        raise


def get_db():
    """Compatibility function for routers that expect db parameter"""
    return None
