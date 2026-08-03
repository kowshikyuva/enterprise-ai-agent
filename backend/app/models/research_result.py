from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database.database import Base


class ResearchResult(Base):
    """The final, project-level executive report compiled from all conclusions."""

    __tablename__ = "research_results"

    id = Column(Integer, primary_key=True, index=True)
    report = Column(Text)
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("ResearchProject", back_populates="results")
