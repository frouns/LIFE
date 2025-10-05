from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List
import json
from starlette.middleware.sessions import SessionMiddleware

from knowledge_base import models, schemas, service
from knowledge_base.database import SessionLocal, engine, get_db
from knowledge_base.auth_service import auth_service

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LIFE API",
    description="API for interacting with the LIFE Knowledge Base.",
    version="1.0.0",
)

# This is a simple way to manage sessions for the auth flow.
# In a production app, you'd use a more robust secret management strategy.
app.add_middleware(
    SessionMiddleware,
    secret_key="a_very_secret_key_for_session_management"
)

knowledge_service = service.KnowledgeService()

# --- Dependency for getting the current user ---
def get_current_user_id(request: Request) -> str:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

# --- Authentication Endpoints ---

@app.get("/api/auth/google/authorize")
def google_authorize():
    authorization_url, state = auth_service.get_authorization_url()
    # Store state in session to prevent CSRF
    return RedirectResponse(authorization_url)

@app.get("/api/auth/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    # The full URL is needed by the OAuth2 flow to validate the request.
    authorization_response = str(request.url)
    credentials_json = auth_service.fetch_token(authorization_response)

    # Use credentials to get user info
    user_info = auth_service.get_user_info(credentials_json)

    user_id = user_info.get("id")
    user_email = user_info.get("email")

    if not user_id or not user_email:
        raise HTTPException(status_code=400, detail="Could not retrieve user info from Google")

    # Create or update user in our database
    db_user = knowledge_service.get_user(db, user_id=user_id)
    if not db_user:
        knowledge_service.create_user(db, user=schemas.UserCreate(id=user_id, email=user_email))

    knowledge_service.update_user_credentials(db, user_id=user_id, credentials_json=credentials_json)

    # Store user ID in session
    request.session["user_id"] = user_id

    # Redirect to the frontend
    return RedirectResponse(url="/")

# --- User Endpoints ---

@app.get("/api/users/me", response_model=schemas.User)
def read_users_me(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = knowledge_service.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Notes Endpoints (Now User-Aware) ---

@app.post("/api/notes/", response_model=schemas.Note, status_code=201)
def create_note(note: schemas.NoteCreate, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    db_note = knowledge_service.get_note(db, user_id=user_id, title=note.title)
    if db_note:
        raise HTTPException(status_code=400, detail="Note with this title already exists")
    return knowledge_service.create_note(db=db, user_id=user_id, note=note)

@app.get("/api/notes/", response_model=List[schemas.Note])
def read_notes(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return knowledge_service.get_notes(db, user_id=user_id)

@app.get("/api/notes/{title}", response_model=schemas.Note)
def read_note(title: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    db_note = knowledge_service.get_note(db, user_id=user_id, title=title)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@app.put("/api/notes/{title}", response_model=schemas.Note)
def update_note(title: str, note: schemas.NoteUpdate, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    db_note = knowledge_service.update_note(db, user_id=user_id, title=title, note_update=note)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

# --- Task Endpoints (Now User-Aware) ---

@app.get("/api/tasks/", response_model=List[schemas.Task])
def read_tasks(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return knowledge_service.get_tasks(db, user_id=user_id)

@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task_status(task_id: str, status: schemas.TaskStatus, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    db_task = knowledge_service.update_task_status(db, user_id=user_id, task_id=task_id, status=status)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task