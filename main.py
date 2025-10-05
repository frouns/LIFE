from fastapi import FastAPI, HTTPException, Depends
from typing import List
from knowledge_base.core import KnowledgeBase, TaskStatus
from knowledge_base.api_models import (
    Note as NoteResponse,
    NoteCreate,
    NoteUpdate,
    Task as TaskResponse,
    TaskUpdate,
    SearchResult
)
from knowledge_base.search import search_notes

app = FastAPI(
    title="LIFE API",
    description="API for interacting with the LIFE Knowledge Base.",
    version="0.1.0",
)

# This is the single, global instance that the application will use by default.
# The tasks_file and search_index_dir are now specified.
kb_singleton = KnowledgeBase(note_dir="notes", tasks_file="tasks.json", search_index_dir="search_index")

def get_kb() -> KnowledgeBase:
    """Dependency function to get the single knowledge base instance."""
    return kb_singleton

@app.get("/api/notes", response_model=List[NoteResponse])
def list_notes(kb: KnowledgeBase = Depends(get_kb)):
    """
    Lists all notes in the knowledge base, including their associated tasks.
    """
    notes_with_tasks = []
    for note in kb.notes.values():
        note.tasks = [task for task in kb.tasks.values() if task.source_note_title == note.title]
        notes_with_tasks.append(note)
    return notes_with_tasks

@app.post("/api/notes", response_model=NoteResponse, status_code=201)
def create_note(note_in: NoteCreate, kb: KnowledgeBase = Depends(get_kb)):
    """
    Creates a new note. Tasks are parsed from the content.
    """
    try:
        note = kb.create_note(title=note_in.title, content=note_in.content)
        note.tasks = [task for task in kb.tasks.values() if task.source_note_title == note.title]
        return note
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.get("/api/notes/daily", response_model=NoteResponse)
def get_daily_note(kb: KnowledgeBase = Depends(get_kb)):
    """
    Retrieves or creates the daily note, including its associated tasks.
    """
    daily_note = kb.get_or_create_daily_note()
    daily_note.tasks = [task for task in kb.tasks.values() if task.source_note_title == daily_note.title]
    return daily_note

@app.get("/api/notes/{title}", response_model=NoteResponse)
def get_note(title: str, kb: KnowledgeBase = Depends(get_kb)):
    """
    Retrieves a single note by its title, including its associated tasks.
    """
    note = kb.get_note(title)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.tasks = [task for task in kb.tasks.values() if task.source_note_title == title]
    return note

@app.put("/api/notes/{title}", response_model=NoteResponse)
def update_note(title: str, note_in: NoteUpdate, kb: KnowledgeBase = Depends(get_kb)):
    """
    Updates the content of an existing note. Tasks are re-parsed from the new content.
    """
    try:
        kb.update_note_content(title=title, new_content=note_in.content)
        note = kb.get_note(title)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found after update")
        note.tasks = [task for task in kb.tasks.values() if task.source_note_title == title]
        return note
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# --- Task Endpoints ---

@app.get("/api/tasks", response_model=List[TaskResponse])
def list_tasks(kb: KnowledgeBase = Depends(get_kb)):
    """
    Lists all tasks from all notes.
    """
    return list(kb.tasks.values())

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task_status(task_id: str, task_in: TaskUpdate, kb: KnowledgeBase = Depends(get_kb)):
    """
    Updates the status of a specific task.
    """
    task = kb.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = task_in.status
    kb._save_tasks() # Persist the change
    return task

# --- Search Endpoint ---

@app.get("/api/search", response_model=List[SearchResult])
def search(q: str, kb: KnowledgeBase = Depends(get_kb)):
    """
    Performs a full-text search across all notes.
    Returns a list of matching notes with highlighted snippets.
    """
    if not q:
        return []
    results = search_notes(kb.search_index, q)
    return results