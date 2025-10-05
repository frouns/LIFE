import os
import re
import json
import uuid
from datetime import datetime
from enum import Enum
from .search import get_search_index, add_note_to_index

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task:
    """Represents a single task, linked to a source note."""
    def __init__(self, description: str, source_note_title: str, status: TaskStatus = TaskStatus.TODO):
        self.id = str(uuid.uuid4())
        self.description = description
        self.source_note_title = source_note_title
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "source_note_title": self.source_note_title,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict):
        task = cls(
            description=data["description"],
            source_note_title=data["source_note_title"],
            status=TaskStatus(data["status"]),
        )
        task.id = data["id"]
        return task

class Note:
    """Represents a single note in the knowledge base."""
    def __init__(self, title: str, content: str = ""):
        if not title:
            raise ValueError("Note title cannot be empty.")
        self.title = title
        self.content = content
        self.links = set()
        self.backlinks = set()

    def __repr__(self):
        return f"Note(title='{self.title}')"

class KnowledgeBase:
    """Manages the collection of notes, tasks, and the search index."""
    def __init__(self, note_dir: str = "notes", tasks_file: str = "tasks.json", search_index_dir: str = "search_index"):
        self.note_dir = note_dir
        self.tasks_file = tasks_file
        self.search_index_dir = search_index_dir

        self.notes = {}
        self.tasks = {}  # In-memory store for tasks, keyed by ID
        self.search_index = get_search_index(self.search_index_dir)

        if not os.path.exists(self.note_dir):
            os.makedirs(self.note_dir)

        self._load_tasks()
        self._load_notes()
        self._build_search_index()

    def _load_tasks(self):
        """Loads tasks from the tasks.json file."""
        if not os.path.exists(self.tasks_file):
            return
        with open(self.tasks_file, "r", encoding="utf-8") as f:
            try:
                tasks_data = json.load(f)
                for task_id, task_dict in tasks_data.items():
                    self.tasks[task_id] = Task.from_dict(task_dict)
            except json.JSONDecodeError:
                # Handle empty or invalid JSON file
                print(f"Warning: Could not decode JSON from {self.tasks_file}. Starting with empty task list.")
                self.tasks = {}


    def _save_tasks(self):
        """Saves the current tasks to the tasks.json file."""
        data_to_save = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4)

    def _load_notes(self):
        """Loads all notes from the note directory."""
        for filename in os.listdir(self.note_dir):
            if filename.endswith(".md"):
                title = os.path.splitext(filename)[0]
                filepath = os.path.join(self.note_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                note = Note(title, content)
                self.notes[title] = note
        self._rebuild_links()

    def _build_search_index(self):
        """Builds the search index from all notes."""
        writer = self.search_index.writer()
        for note in self.notes.values():
            writer.update_document(
                title=note.title,
                content=note.content
            )
        writer.commit()

    def _rebuild_links(self):
        """Rebuilds links and backlinks from note content."""
        link_pattern = re.compile(r"\[\[(.*?)\]\]")
        # First, clear all links and establish forward links from content
        for note in self.notes.values():
            note.links.clear()
            note.backlinks.clear()
            note.links.update(link_pattern.findall(note.content))

        # Second, build all backlinks
        for note in self.notes.values():
            for linked_title in note.links:
                target_note = self.get_note(linked_title)
                if target_note:
                    target_note.backlinks.add(note.title)

    def get_note(self, title: str) -> Note | None:
        """Gets a note by its title."""
        return self.notes.get(title)

    def _parse_and_update_tasks_from_note(self, note: Note):
        """Parses a note's content for /todo tasks and updates the central task list."""
        task_pattern = re.compile(r"\/todo\s+(.*)", re.MULTILINE)

        # Find all task descriptions in the current note content
        found_descriptions = set(task_pattern.findall(note.content))

        # Find all existing task objects linked to this note
        existing_tasks_for_note = [task for task in self.tasks.values() if task.source_note_title == note.title]
        existing_descriptions = {task.description for task in existing_tasks_for_note}

        # Add new tasks
        for desc in found_descriptions - existing_descriptions:
            new_task = Task(description=desc, source_note_title=note.title)
            self.tasks[new_task.id] = new_task

        # Remove old tasks
        tasks_to_remove = [task for task in existing_tasks_for_note if task.description not in found_descriptions]
        for task in tasks_to_remove:
            del self.tasks[task.id]

    def create_note(self, title: str, content: str = "") -> Note:
        """Creates a new note, saves it, and updates links, tasks, and the search index."""
        if title in self.notes:
            raise ValueError(f"Note with title '{title}' already exists.")

        note = Note(title, content)
        self.notes[title] = note
        self._update_links_from_note(note)
        self._parse_and_update_tasks_from_note(note)
        self.save_note(note)
        self._save_tasks()
        add_note_to_index(self.search_index, note)
        return note

    def update_note_content(self, title: str, new_content: str):
        """Updates the content of a note and rebuilds links, tasks, and the search index."""
        note = self.get_note(title)
        if not note:
            raise ValueError(f"Note with title '{title}' not found.")

        note.content = new_content
        self._rebuild_links() # Rebuild all links to ensure consistency
        self._parse_and_update_tasks_from_note(note)
        self.save_note(note)
        self._save_tasks()
        add_note_to_index(self.search_index, note)

    def _update_links_from_note(self, note: Note):
        """Parses a note's content and updates links and backlinks."""
        link_pattern = re.compile(r"\[\[(.*?)\]\]")
        linked_titles = set(link_pattern.findall(note.content))

        # Update forward links for the current note
        note.links = linked_titles

        # Update backlinks for all other notes
        self._rebuild_links()

    def get_or_create_daily_note(self) -> Note:
        """Gets or creates the note for the current day."""
        today_title = datetime.now().strftime("%Y-%m-%d")
        note = self.get_note(today_title)
        if not note:
            note = self.create_note(today_title, f"# Daily Note for {today_title}\n\n")
        return note

    def save_note(self, note: Note):
        """Saves a single note to the filesystem."""
        filepath = os.path.join(self.note_dir, f"{note.title}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(note.content)