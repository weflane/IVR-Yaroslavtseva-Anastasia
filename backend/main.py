from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routers import auth, books, quiz, library, comments, tags, recommendations
from app.database import init_db 

app = FastAPI(title="BookMatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(quiz.router)
app.include_router(library.router)
app.include_router(comments.router)
app.include_router(tags.router)
app.include_router(recommendations.router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}