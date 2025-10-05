from sqlalchemy.orm import Session
from . import models, schemas
import uuid
import re

class KnowledgeService:
    def get_note(self, db: Session, title: str):
        return db.query(models.Note).filter(models.Note.title == title).first()

    def get_notes(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Note).offset(skip).limit(limit).all()

    def create_note(self, db: Session, note: schemas.NoteCreate):
        db_note = models.Note(title=note.title, content=note.content)
        db.add(db_note)
        self._parse_and_update_tasks(db, db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    def update_note(self, db: Session, title: str, note_update: schemas.NoteUpdate):
        db_note = self.get_note(db, title)
        if not db_note:
            return None
        db_note.content = note_update.content
        self._parse_and_update_tasks(db, db_note)
        db.commit()
        db.refresh(db_note)
        return db_note

    def get_tasks(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Task).offset(skip).limit(limit).all()

    def update_task_status(self, db: Session, task_id: str, status: models.TaskStatus):
        db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not db_task:
            return None
        db_task.status = status
        db.commit()
        db.refresh(db_task)
        return db_task

    def _parse_and_update_tasks(self, db: Session, note: models.Note):
        """Parses a note's content for /todo tasks and updates the database."""
        task_pattern = re.compile(r"\/todo\s+(.*)", re.MULTILINE)
        found_descriptions = set(task_pattern.findall(note.content))

        # In a DB context, it's easier to manage by relationship
        existing_tasks = {task.description: task for task in note.tasks}

        # Add new tasks
        for desc in found_descriptions:
            if desc not in existing_tasks:
                new_task = models.Task(
                    id=str(uuid.uuid4()),
                    description=desc,
                    source_note_title=note.title
                )
                db.add(new_task)

        # Remove old tasks
        for desc, task in existing_tasks.items():
            if desc not in found_descriptions:
                db.delete(task)

# We will also need to update our Pydantic models for this new structure.
# I'll create a schemas.py file for this.
# This is a logical grouping of the new service layer.
knowledge_service = KnowledgeService()