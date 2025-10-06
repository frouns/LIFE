from sqlalchemy.orm import Session
from . import models, schemas
import uuid
import re

class KnowledgeService:
    # --- User Methods ---
    def get_user(self, db: Session, user_id: str):
        return db.query(models.User).filter(models.User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    def create_user(self, db: Session, user: schemas.UserCreate):
        db_user = models.User(id=user.id, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user_credentials(self, db: Session, user_id: str, credentials_json: str):
        db_user = self.get_user(db, user_id)
        if not db_user:
            return None
        db_user.google_credentials = credentials_json
        db.commit()
        db.refresh(db_user)
        return db_user

    # --- Note Methods (User-Aware) ---
    def get_note(self, db: Session, user_id: str, title: str):
        return db.query(models.Note).filter(models.Note.title == title, models.Note.owner_id == user_id).first()

    def get_notes(self, db: Session, user_id: str, skip: int = 0, limit: int = 100):
        return db.query(models.Note).filter(models.Note.owner_id == user_id).offset(skip).limit(limit).all()

    def create_note(self, db: Session, user_id: str, note: schemas.NoteCreate):
        db_note = models.Note(title=note.title, content=note.content, owner_id=user_id)
        db.add(db_note)
        self._parse_and_update_tasks(db, db_note, user_id)
        db.commit()
        db.refresh(db_note)
        return db_note

    def update_note(self, db: Session, user_id: str, title: str, note_update: schemas.NoteUpdate):
        db_note = self.get_note(db, user_id, title)
        if not db_note:
            return None
        db_note.content = note_update.content
        self._parse_and_update_tasks(db, db_note, user_id)
        db.commit()
        db.refresh(db_note)
        return db_note

    # --- Task Methods (User-Aware) ---
    def get_tasks(self, db: Session, user_id: str, skip: int = 0, limit: int = 100):
        return db.query(models.Task).filter(models.Task.owner_id == user_id).offset(skip).limit(limit).all()

    def update_task_status(self, db: Session, user_id: str, task_id: str, status: models.TaskStatus):
        db_task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()
        if not db_task:
            return None
        db_task.status = status
        db.commit()
        db.refresh(db_task)
        return db_task

    def _parse_and_update_tasks(self, db: Session, note: models.Note, user_id: str):
        task_pattern = re.compile(r"\/todo\s+(.*)", re.MULTILINE)
        found_descriptions = set(task_pattern.findall(note.content))

        existing_tasks = {task.description: task for task in note.tasks}

        for desc in found_descriptions:
            if desc not in existing_tasks:
                new_task = models.Task(
                    id=str(uuid.uuid4()),
                    description=desc,
                    source_note_title=note.title,
                    owner_id=user_id
                )
                db.add(new_task)

        for desc, task in existing_tasks.items():
            if desc not in found_descriptions:
                db.delete(task)

knowledge_service = KnowledgeService()