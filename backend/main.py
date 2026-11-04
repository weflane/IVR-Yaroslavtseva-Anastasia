import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.database import init_db
from app.routers import auth, books, comments, library, quiz, recommendations, tags


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="BookMatch API", lifespan=lifespan)

allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    if o.strip()
]

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(quiz.router)
app.include_router(library.router)
app.include_router(comments.router)
app.include_router(tags.router)
app.include_router(recommendations.router)


@app.get("/health")
def health():
    return {"status": "ok"}
