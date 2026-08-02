from app.database.database import Base, engine

from app.models.user import User
from app.models.research_project import ResearchProject
from app.models.document import Document
from app.models.research_result import ResearchResult
from app.models.source import Source

print(Base.metadata.tables.keys())

Base.metadata.create_all(bind=engine)

print("All tables created successfully!")