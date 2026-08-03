from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Contradiction(Base):
    """Flags two findings on the same question that disagree (Stage 8: Detect Contradictions)."""

    __tablename__ = "contradictions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("research_questions.id"), nullable=False)
    finding_a_id = Column(Integer, ForeignKey("findings.id"), nullable=False)
    finding_b_id = Column(Integer, ForeignKey("findings.id"), nullable=False)
    explanation = Column(Text, nullable=False)

    question = relationship("ResearchQuestion", back_populates="contradictions")
    finding_a = relationship("Finding", foreign_keys=[finding_a_id])
    finding_b = relationship("Finding", foreign_keys=[finding_b_id])
