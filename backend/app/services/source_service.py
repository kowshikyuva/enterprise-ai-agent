from sqlalchemy.orm import Session
from app.models.source import Source


def save_source(db: Session, title: str, url: str, content: str):
    existing = db.query(Source).filter(Source.url == url).first()

    if existing:
        return existing

    source = Source(
        title=title,
        url=url,
        content=content
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source