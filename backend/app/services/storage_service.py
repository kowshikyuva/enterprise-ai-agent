from sqlalchemy.orm import Session
from app.repositories.source_repository import SourceRepository

def save_source(db: Session, title, url, content):
    return SourceRepository.create(
        db,
        title,
        url,
        content
    )