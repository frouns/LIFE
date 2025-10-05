from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from knowledge_base import models, schemas, service
from knowledge_base.database import SessionLocal, engine, get_db

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LIFE API",
    description="API for interacting with the LIFE Knowledge Base.",
    version="1.0.0",
)

knowledge_service = service.KnowledgeService()

# --- Notes Endpoints ---

@app.post("/api/notes/", response_model=schemas.Note, status_code=201)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = knowledge_service.get_note(db, title=note.title)
    if db_note:
        raise HTTPException(status_code=400, detail="Note with this title already exists")
    return knowledge_service.create_note(db=db, note=note)

@app.get("/api/notes/", response_model=List[schemas.Note])
def read_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    notes = knowledge_service.get_notes(db, skip=skip, limit=limit)
    return notes

@app.get("/api/notes/{title}", response_model=schemas.Note)
def read_note(title: str, db: Session = Depends(get_db)):
    db_note = knowledge_service.get_note(db, title=title)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@app.put("/api/notes/{title}", response_model=schemas.Note)
def update_note(title: str, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    db_note = knowledge_service.update_note(db, title=title, note_update=note)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

# --- Task Endpoints ---

@app.get("/api/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = knowledge_service.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task_status(task_id: str, status: schemas.TaskStatus, db: Session = Depends(get_db)):
    db_task = knowledge_service.update_task_status(db, task_id=task_id, status=status)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task