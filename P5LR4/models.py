from sqlalchemy import Column, Integer, String, Text
from database import Base

class Term(Base):
    __tablename__ = "terms"
    
    id = Column(Integer, primary_key=True, index=True)
    term = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, default="Общие")
    example = Column(Text, nullable=True)