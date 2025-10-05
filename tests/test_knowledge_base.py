import unittest
import os
import shutil
from datetime import datetime
from knowledge_base.core import KnowledgeBase, Note

class TestKnowledgeBase(unittest.TestCase):

    def setUp(self):
        """Set up a temporary test environment."""
        self.test_dir = "test_notes"
        os.makedirs(self.test_dir, exist_ok=True)
        self.kb = KnowledgeBase(note_dir=self.test_dir)

    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.test_dir)

    def test_create_note(self):
        """Test creating a single note."""
        note = self.kb.create_note("Test Note", "This is a test.")
        self.assertIn("Test Note", self.kb.notes)
        self.assertEqual(note.content, "This is a test.")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Test Note.md")))

    def test_create_note_with_empty_title_raises_error(self):
        """Test that creating a note with an empty title raises a ValueError."""
        with self.assertRaises(ValueError):
            self.kb.create_note("", "This should fail.")

    def test_create_duplicate_note_raises_error(self):
        """Test that creating a note with a duplicate title raises a ValueError."""
        self.kb.create_note("Duplicate", "First note.")
        with self.assertRaises(ValueError):
            self.kb.create_note("Duplicate", "Second note.")

    def test_bidirectional_linking_on_create(self):
        """Test that links are created correctly when a new note is made."""
        self.kb.create_note("Note A", "This is a note.")
        self.kb.create_note("Note B", "This links to [[Note A]].")

        note_a = self.kb.get_note("Note A")
        note_b = self.kb.get_note("Note B")

        self.assertIn("Note A", note_b.links)
        self.assertIn("Note B", note_a.backlinks)

    def test_bidirectional_linking_on_update(self):
        """Test that links are updated correctly when a note's content changes."""
        note_a = self.kb.create_note("Note A", "Initial content.")
        note_b = self.kb.create_note("Note B", "Initial content.")

        self.kb.update_note_content("Note A", "Now linking to [[Note B]].")

        self.assertIn("Note B", note_a.links)
        self.assertIn("Note A", note_b.backlinks)

        # Test link removal
        self.kb.update_note_content("Note A", "Links removed.")
        self.assertNotIn("Note B", note_a.links)
        self.assertNotIn("Note A", note_b.backlinks)

    def test_daily_note_creation(self):
        """Test the get_or_create_daily_note method."""
        daily_note = self.kb.get_or_create_daily_note()
        today_title = datetime.now().strftime("%Y-%m-%d")

        self.assertEqual(daily_note.title, today_title)
        self.assertIn(today_title, self.kb.notes)

        # Test that calling it again returns the same note
        same_daily_note = self.kb.get_or_create_daily_note()
        self.assertIs(daily_note, same_daily_note)

    def test_loading_from_files(self):
        """Test that the knowledge base correctly loads from existing files."""
        # Create files manually to simulate a pre-existing knowledge base
        with open(os.path.join(self.test_dir, "File A.md"), "w") as f:
            f.write("This links to [[File B]].")
        with open(os.path.join(self.test_dir, "File B.md"), "w") as f:
            f.write("This is File B.")

        # Create a new KB instance to trigger loading from files
        new_kb = KnowledgeBase(note_dir=self.test_dir)
        self.assertIn("File A", new_kb.notes)
        self.assertIn("File B", new_kb.notes)

        note_a = new_kb.get_note("File A")
        note_b = new_kb.get_note("File B")

        self.assertIn("File B", note_a.links)
        self.assertIn("File A", note_b.backlinks)

if __name__ == "__main__":
    unittest.main()