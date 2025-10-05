from fastapi import FastAPI
from knowledge_base.core import KnowledgeBase
from knowledge_base.api_models import Note as NoteResponse

app = FastAPI(
    title="LIFE API",
    description="API for interacting with the LIFE Knowledge Base.",
    version="0.1.0",
)

# Initialize the Knowledge Base
# This will load all existing notes from the 'notes' directory
kb = KnowledgeBase(note_dir="notes")

@app.get("/api/notes/daily", response_model=NoteResponse)
def get_daily_note():
    """
    Retrieves or creates the daily note.
    """
    daily_note = kb.get_or_create_daily_note()
    return daily_note