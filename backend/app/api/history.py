from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.source import Source
from app.models.research_project import ResearchProject

router = APIRouter()


@router.get("/history")
def history(db: Session = Depends(get_db)):
    """All sources ever collected — the reusable knowledge base."""
    return db.query(Source).all()


@router.get("/projects")
def projects(db: Session = Depends(get_db)):
    """List past research runs so the pipeline output can be revisited via
    GET /research/{project_id}."""
    rows = db.query(ResearchProject).order_by(ResearchProject.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "topic": p.topic,
            "status": p.status,
            "created_at": p.created_at,
            "question_count": len(p.questions),
        }
        for p in rows
    ]
