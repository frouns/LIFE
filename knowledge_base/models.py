from sqlalchemy import Column, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum

class Note(Base):
    __tablename__ = "notes"

    title = Column(String, primary_key=True, index=True)
    content = Column(String, default="")

    tasks = relationship("Task", back_populates="source_note")

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    description = Column(String, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)

    source_note_title = Column(String, ForeignKey("notes.title"))
    source_note = relationship("Note", back_populates="tasks")