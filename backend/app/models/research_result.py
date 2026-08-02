from sqlalchemy import Column, Integer, Text, ForeignKey
from app.database.database import Base

class ResearchResult(Base):
    __tablename__ = "research_results"

    id = Column(Integer, primary_key=True, index=True)
    report = Column(Text)
    project_id = Column(Integer, ForeignKey("research_projects.id"))