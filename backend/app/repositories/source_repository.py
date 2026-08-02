from sqlalchemy.orm import Session
from app.models.source import Source

class SourceRepository:

    @staticmethod
    def create(db: Session, title: str, url: str, content: str):

        source = Source(
            title=title,
            url=url,
            content=content
        )

        db.add(source)
        db.commit()
        db.refresh(source)

        return source