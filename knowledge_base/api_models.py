from pydantic import BaseModel
from typing import Set, Optional

class Note(BaseModel):
    """Pydantic model for representing a Note in the API."""
    title: str
    content: str
    links: Set[str]
    backlinks: Set[str]

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    """Pydantic model for creating a new note."""
    title: str
    content: Optional[str] = ""

class NoteUpdate(BaseModel):
    """Pydantic model for updating a note's content."""
    content: str