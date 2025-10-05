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
        self.notes = {}
        if not os.path.exists(self.note_dir):
            os.makedirs(self.note_dir)
        self._load_notes()

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

    def create_note(self, title: str, content: str = "") -> Note:
        """Creates a new note, saves it, and updates links."""
        if title in self.notes:
            raise ValueError(f"Note with title '{title}' already exists.")

        note = Note(title, content)
        self.notes[title] = note
        self._update_links_from_note(note)
        self.save_note(note)
        return note

    def update_note_content(self, title: str, new_content: str):
        """Updates the content of a note and rebuilds links."""
        note = self.get_note(title)
        if not note:
            raise ValueError(f"Note with title '{title}' not found.")

        note.content = new_content
        self._rebuild_links() # Rebuild all links to ensure consistency
        self.save_note(note)

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