from fastapi import FastAPI, HTTPException, Depends
from typing import List
from knowledge_base.core import KnowledgeBase
from knowledge_base.api_models import Note as NoteResponse, NoteCreate, NoteUpdate

app = FastAPI(
    title="LIFE API",
    description="API for interacting with the LIFE Knowledge Base.",
    version="0.1.0",
)

# This is the single, global instance that the application will use by default.
kb_singleton = KnowledgeBase(note_dir="notes")

def get_kb() -> KnowledgeBase:
    """Dependency function to get the single knowledge base instance."""
    return kb_singleton

@app.get("/api/notes", response_model=List[NoteResponse])
def list_notes(kb: KnowledgeBase = Depends(get_kb)):
    """
    Lists all notes in the knowledge base.
    """
    return list(kb.notes.values())

@app.post("/api/notes", response_model=NoteResponse, status_code=201)
def create_note(note_in: NoteCreate, kb: KnowledgeBase = Depends(get_kb)):
    """
    Creates a new note.
    A 409 Conflict error is returned if a note with the same title already exists.
    """
    try:
        note = kb.create_note(title=note_in.title, content=note_in.content)
        return note
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/api/notes/daily", response_model=NoteResponse)
def get_daily_note(kb: KnowledgeBase = Depends(get_kb)):
    """
    Retrieves or creates the daily note.
    """
    daily_note = kb.get_or_create_daily_note()
    return daily_note

@app.get("/api/notes/{title}", response_model=NoteResponse)
def get_note(title: str, kb: KnowledgeBase = Depends(get_kb)):
    """
    Retrieves a single note by its title.
    A 404 Not Found error is returned if the note does not exist.
    """
    note = kb.get_note(title)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/api/notes/{title}", response_model=NoteResponse)
def update_note(title: str, note_in: NoteUpdate, kb: KnowledgeBase = Depends(get_kb)):
    """
    Updates the content of an existing note.
    A 404 Not Found error is returned if the note does not exist.
    """
    try:
        kb.update_note_content(title=title, new_content=note_in.content)
        note = kb.get_note(title)
        if not note:
            # This case should ideally not be hit if update_note_content raises an error
            raise HTTPException(status_code=404, detail="Note not found after update")
        return note
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))