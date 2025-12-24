from pydantic import BaseModel
from typing import Optional

class TermBase(BaseModel):
    term: str
    description: str
    category: Optional[str] = "Общие"
    example: Optional[str] = None

class TermCreate(TermBase):
    pass

class TermUpdate(BaseModel):
    description: Optional[str] = None
    category: Optional[str] = None
    example: Optional[str] = None

class TermResponse(TermBase):
    id: int
    
    class Config:
        from_attributes = True