from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine

# Import models
from app.models.user import User
from app.models.research_project import ResearchProject
from app.models.document import Document
from app.models.research_result import ResearchResult
from app.models.source import Source

# Import routers
from app.api.research import router as research_router
from app.api.chat import router as chat_router
from app.api.history import router as history_router
from app.api.stats import router as stats_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Enterprise AI Research Agent",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(research_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(stats_router)

@app.get("/")
def root():
    return {
        "message": "Enterprise AI Research Agent is running successfully!"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }