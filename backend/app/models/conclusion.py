from sqlalchemy import Column, Integer, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database.database import Base

# Many-to-many join so every conclusion is traceable back to the exact
# findings (and therefore sources) that back it up (Stage 10: Traceability).
conclusion_findings = Table(
    "conclusion_findings",
    Base.metadata,
    Column("conclusion_id", Integer, ForeignKey("conclusions.id"), primary_key=True),
    Column("finding_id", Integer, ForeignKey("findings.id"), primary_key=True),
)


class Conclusion(Base):
    """The synthesized answer for one research question (Stage 9: Generate Conclusions)."""

    __tablename__ = "conclusions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("research_questions.id"), nullable=False, unique=True)
    summary = Column(Text, nullable=False)

    question = relationship("ResearchQuestion", back_populates="conclusion")
    supporting_findings = relationship("Finding", secondary=conclusion_findings)
