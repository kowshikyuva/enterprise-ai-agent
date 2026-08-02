from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.source import Source
from app.services.chroma_service import collection

router = APIRouter()

@router.get("/stats")
def stats(db: Session = Depends(get_db)):

    return {
        "postgres_sources": db.query(Source).count(),
        "vector_documents": collection.count(),
        "status": "Healthy"
    }