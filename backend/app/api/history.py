from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.source import Source

router = APIRouter()

@router.get("/history")
def history(db: Session = Depends(get_db)):
    return db.query(Source).all()