from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="pending")  # pending -> running -> completed -> failed
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship("ResearchQuestion", back_populates="project", cascade="all, delete-orphan")
    results = relationship("ResearchResult", back_populates="project", cascade="all, delete-orphan")
