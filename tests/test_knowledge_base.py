import unittest
import os
import shutil
from datetime import datetime
from knowledge_base.core import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):

    def setUp(self):
        """Set up a temporary test environment."""
        self.test_dir = "test_notes"
        # Start with a clean directory for each test
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.kb = KnowledgeBase(note_dir=self.test_dir)

    def tearDown(self):
        """Clean up the test environment."""
        shutil.rmtree(self.test_dir)

    def test_create_and_get_note(self):
        """Test creating a single note and retrieving it."""
        note = self.kb.create_note("Test Note", "This is a test.")
        self.assertIn("Test Note", self.kb.notes)
        retrieved_note = self.kb.get_note("Test Note")
        self.assertIsNotNone(retrieved_note)
        self.assertEqual(retrieved_note.content, "This is a test.")
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Test Note.md")))

    def test_bidirectional_linking(self):
        """Test that links are created correctly between notes."""
        note_a = self.kb.create_note("Note A", "This links to [[Note B]].")
        note_b = self.kb.create_note("Note B", "This is linked from [[Note A]].")

        # After creation, the links should be established.
        self.assertIn("Note B", note_a.links)
        self.assertIn("Note A", note_b.backlinks)
        self.assertIn("Note A", note_b.links)
        self.assertIn("Note B", note_a.backlinks)

    def test_link_to_nonexistent_note(self):
        """Test that linking to a non-existent note does not create a link."""
        note_a = self.kb.create_note("Note A", "This links to [[Non-existent Note]].")
        self.assertNotIn("Non-existent Note", note_a.links)

    def test_daily_note_creation(self):
        """Test the get_or_create_daily_note method."""
        daily_note = self.kb.get_or_create_daily_note()
        today_title = datetime.now().strftime("%Y-%m-%d")

        self.assertEqual(daily_note.title, today_title)
        self.assertIn(today_title, self.kb.notes)

        # Test that calling it again returns the same note object
        same_daily_note = self.kb.get_or_create_daily_note()
        self.assertIs(daily_note, same_daily_note)

    def test_loading_from_files(self):
        """Test that the knowledge base correctly loads from existing files and builds links."""
        # Manually create files to simulate a pre-existing state
        notes_dir = "test_load_dir"
        os.makedirs(notes_dir, exist_ok=True)
        with open(os.path.join(notes_dir, "File A.md"), "w") as f:
            f.write("Content with a link to [[File B]].")
        with open(os.path.join(notes_dir, "File B.md"), "w") as f:
            f.write("Content of file B.")

        # Create a new KB instance to trigger loading from files
        kb_loaded = KnowledgeBase(note_dir=notes_dir)
        self.assertIn("File A", kb_loaded.notes)
        self.assertIn("File B", kb_loaded.notes)

        note_a = kb_loaded.get_note("File A")
        note_b = kb_loaded.get_note("File B")

        self.assertIn("File B", note_a.links)
        self.assertIn("File A", note_b.backlinks)

        # Clean up the temporary directory
        shutil.rmtree(notes_dir)

if __name__ == "__main__":
    unittest.main()