from pydantic import BaseModel
from typing import Set

class Note(BaseModel):
    """Pydantic model for representing a Note in the API."""
    title: str
    content: str
    links: Set[str]
    backlinks: Set[str]

    class Config:
        from_attributes = True