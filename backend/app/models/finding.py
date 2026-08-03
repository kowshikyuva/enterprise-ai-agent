from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.database import Base


class Finding(Base):
    """A single extracted claim/fact tied to one source and one question
    (Stages 5 & 7: Extract Findings, Classify Findings)."""

    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("research_questions.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    content = Column(Text, nullable=False)
    classification = Column(String, default="other")  # benefit | challenge | trend | statistic | risk | other
    confidence = Column(Float, default=0.5)  # 0-1, how strongly the source supports this finding

    question = relationship("ResearchQuestion", back_populates="findings")
    source = relationship("Source")
