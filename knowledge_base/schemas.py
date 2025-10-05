from pydantic import BaseModel
from typing import List, Optional
from .models import TaskStatus

# Pydantic models for Tasks

class TaskBase(BaseModel):
    description: str
    status: TaskStatus = TaskStatus.TODO

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    source_note_title: str

    class Config:
        orm_mode = True

# Pydantic models for Notes

class NoteBase(BaseModel):
    title: str

class NoteCreate(NoteBase):
    content: Optional[str] = ""

class NoteUpdate(BaseModel):
    content: str

class Note(NoteBase):
    content: Optional[str] = ""
    tasks: List[Task] = []

    class Config:
        orm_mode = True