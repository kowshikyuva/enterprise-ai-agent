from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class ResearchQuestion(Base):
    """A sub-question the topic was decomposed into (Stage 1: Define Research Questions)."""

    __tablename__ = "research_questions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id"), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, default=0)

    project = relationship("ResearchProject", back_populates="questions")
    findings = relationship("Finding", back_populates="question", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="question", cascade="all, delete-orphan")
    conclusion = relationship("Conclusion", back_populates="question", uselist=False, cascade="all, delete-orphan")
