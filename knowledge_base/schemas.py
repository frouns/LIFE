from pydantic import BaseModel
from typing import List, Optional
from .models import TaskStatus

# --- Task Schemas ---

class TaskBase(BaseModel):
    description: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    status: TaskStatus

class Task(TaskBase):
    id: str
    status: TaskStatus
    source_note_title: str

    class Config:
        orm_mode = True

# --- Note Schemas ---

class NoteBase(BaseModel):
    title: str

class NoteCreate(NoteBase):
    content: Optional[str] = ""

class NoteUpdate(BaseModel):
    content: str

class Note(NoteBase):
    content: Optional[str]
    tasks: List[Task] = []

    class Config:
        orm_mode = True

# --- User Schemas ---

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    id: str # The user ID will be provided by the auth system (e.g., Google ID)

class User(UserBase):
    id: str
    notes: List[Note] = []
    tasks: List[Task] = []

    class Config:
        orm_mode = True