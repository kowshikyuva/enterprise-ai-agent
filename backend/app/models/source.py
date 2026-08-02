from sqlalchemy import Column, Integer, String, Text
from app.database.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    url = Column(String, unique=True)
    content = Column(Text)