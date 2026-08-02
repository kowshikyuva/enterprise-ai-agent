from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.research import ResearchRequest
from app.services.research_service import run_research

router = APIRouter()

@router.post("/research")
def research(request: ResearchRequest, db: Session = Depends(get_db)):
    return run_research(request.topic, db)