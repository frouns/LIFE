from pydantic import BaseModel
from typing import Set, Optional, List
from .core import TaskStatus

class Task(BaseModel):
    """Pydantic model for representing a Task in the API."""
    id: str
    description: str
    source_note_title: str
    status: TaskStatus

    class Config:
        from_attributes = True

class SearchResult(BaseModel):
    """Pydantic model for a single search result."""
    title: str
    snippet: str
    score: float

class TaskUpdate(BaseModel):
    """Pydantic model for updating a task's status."""
    status: TaskStatus

class Note(BaseModel):
    """Pydantic model for representing a Note in the API."""
    title: str
    content: str
    links: Set[str]
    backlinks: Set[str]
    tasks: List[Task] = []

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    """Pydantic model for creating a new note."""
    title: str
    content: Optional[str] = ""

class NoteUpdate(BaseModel):
    """Pydantic model for updating a note's content."""
    content: str