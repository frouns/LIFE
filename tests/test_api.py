import unittest
import os
import shutil
from fastapi.testclient import TestClient

from main import app, get_kb
from knowledge_base.core import KnowledgeBase

TEST_NOTES_DIR = "test_api_notes"

class TestApi(unittest.TestCase):

    def setUp(self):
        """
        Set up a clean environment for each test.
        This runs before every single test function.
        """
        # 1. Ensure the test directory is clean.
        if os.path.exists(TEST_NOTES_DIR):
            shutil.rmtree(TEST_NOTES_DIR)
        os.makedirs(TEST_NOTES_DIR)

        # 2. Create a fresh KnowledgeBase instance for this specific test.
        self.kb_instance = KnowledgeBase(note_dir=TEST_NOTES_DIR)

        # 3. Define a function that will return our test-specific KB instance.
        def get_kb_override():
            return self.kb_instance

        # 4. Apply the override to the FastAPI app.
        app.dependency_overrides[get_kb] = get_kb_override

        # 5. Create a new TestClient that uses the overridden app.
        self.client = TestClient(app)

    def tearDown(self):
        """
        Clean up after each test.
        """
        # Clear the dependency overrides to not affect other tests or modules
        app.dependency_overrides.clear()
        # Clean up the test directory
        if os.path.exists(TEST_NOTES_DIR):
            shutil.rmtree(TEST_NOTES_DIR)

    def test_create_note(self):
        """Test creating a note via the API."""
        response = self.client.post("/api/notes", json={"title": "Test Note", "content": "Hello, API!"})
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Test Note")
        self.assertEqual(data["content"], "Hello, API!")
        # Verify it was actually created
        self.assertIn("Test Note", self.kb_instance.notes)

    def test_create_duplicate_note_fails(self):
        """Test that creating a note with a duplicate title fails."""
        self.client.post("/api/notes", json={"title": "Duplicate", "content": "First"})
        response = self.client.post("/api/notes", json={"title": "Duplicate", "content": "Second"})
        self.assertEqual(response.status_code, 409)

    def test_get_note(self):
        """Test retrieving a single note."""
        self.kb_instance.create_note("My Note", "Content")
        response = self.client.get("/api/notes/My Note")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "My Note")

    def test_get_nonexistent_note_fails(self):
        """Test that retrieving a non-existent note fails."""
        response = self.client.get("/api/notes/NonExistent")
        self.assertEqual(response.status_code, 404)

    def test_list_notes(self):
        """Test listing all notes."""
        self.kb_instance.create_note("Note 1", "Content 1")
        self.kb_instance.create_note("Note 2", "Content 2")
        response = self.client.get("/api/notes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual({d["title"] for d in data}, {"Note 1", "Note 2"})

    def test_update_note(self):
        """Test updating a note's content."""
        self.kb_instance.create_note("Original Title", "Original Content")
        response = self.client.put(
            "/api/notes/Original Title",
            json={"content": "Updated Content"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["content"], "Updated Content")

        # Verify the content was actually updated in our isolated KB instance
        updated_note = self.kb_instance.get_note("Original Title")
        self.assertEqual(updated_note.content, "Updated Content")

    def test_update_note_updates_links(self):
        """Test that updating a note correctly updates links and backlinks."""
        self.kb_instance.create_note("Note A", "Initial A")
        self.kb_instance.create_note("Note B", "Initial B")

        # Update Note A to link to Note B
        self.client.put("/api/notes/Note A", json={"content": "Now linking to [[Note B]]"})

        # Check Note B for the backlink in our isolated KB instance
        note_b = self.kb_instance.get_note("Note B")
        self.assertIn("Note A", note_b.backlinks)

    def test_get_daily_note(self):
        """Test retrieving the daily note."""
        from datetime import datetime
        today_title = datetime.now().strftime("%Y-%m-%d")
        response = self.client.get("/api/notes/daily")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], today_title)
        self.assertIn(f"# Daily Note for {today_title}", data["content"])

if __name__ == "__main__":
    unittest.main()