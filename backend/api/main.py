"""
DocMind AI — FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import documents, chat, sessions

# Ensure data directories exist
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/vector_store", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("🚀 DocMind AI starting up...")
    yield
    print("🛑 DocMind AI shutting down...")


app = FastAPI(
    title="DocMind AI",
    description="ChatGPT for your PDFs — RAG-powered document Q&A with citations",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])


@app.get("/")
async def root():
    return {"status": "ok", "message": "DocMind AI is running 🧠"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
