import os
import re
from datetime import datetime

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
    """Manages the collection of notes."""
    def __init__(self, note_dir: str = "notes"):
        self.note_dir = note_dir
        if not os.path.exists(self.note_dir):
            os.makedirs(self.note_dir)
        self.notes = self._load_notes()
        self._rebuild_all_links()

    def _load_notes(self):
        """Loads all notes from the note directory."""
        notes = {}
        for filename in os.listdir(self.note_dir):
            if filename.endswith(".md"):
                title = os.path.splitext(filename)[0]
                filepath = os.path.join(self.note_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                notes[title] = Note(title, content)
        return notes

    def _rebuild_all_links(self):
        """Scans all notes and builds the link/backlink network."""
        for note in self.notes.values():
            note.links.clear()
            note.backlinks.clear()

        for source_note in self.notes.values():
            linked_titles = self._parse_links_from_content(source_note.content)
            for target_title in linked_titles:
                if target_title in self.notes:
                    target_note = self.notes[target_title]
                    source_note.links.add(target_note.title)
                    target_note.backlinks.add(source_note.title)

    def _parse_links_from_content(self, content: str):
        """Finds all [[wiki-style]] links in a block of text."""
        return set(re.findall(r"\[\[(.*?)\]\]", content))

    def get_note(self, title: str):
        """Gets a note by its title."""
        return self.notes.get(title)

    def create_note(self, title: str, content: str = ""):
        """Creates a new note, saves it, and updates the knowledge base."""
        if title in self.notes:
            raise ValueError(f"Note with title '{title}' already exists.")

        note = Note(title, content)
        self.notes[title] = note
        self.save_note(note)
        self._rebuild_all_links()
        return note

    def save_note(self, note: Note):
        """Saves a single note to the filesystem."""
        filepath = os.path.join(self.note_dir, f"{note.title}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(note.content)

    def get_or_create_daily_note(self):
        """Gets or creates the note for the current day."""
        today_title = datetime.now().strftime("%Y-%m-%d")
        note = self.get_note(today_title)
        if not note:
            note = self.create_note(today_title, f"# Daily Note for {today_title}\n\n")
        return note