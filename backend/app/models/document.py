from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    filepath = Column(String)
    project_id = Column(Integer, ForeignKey("research_projects.id"))