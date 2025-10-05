import unittest
import os
import shutil
from fastapi.testclient import TestClient
from datetime import datetime

from main import app, kb

# We need to ensure the test runs in a clean environment.
TEST_NOTES_DIR = "test_api_notes"
kb.note_dir = TEST_NOTES_DIR # Point the global kb to a test directory

class TestApi(unittest.TestCase):

    def setUp(self):
        """Set up a clean notes directory for each test."""
        if os.path.exists(TEST_NOTES_DIR):
            shutil.rmtree(TEST_NOTES_DIR)
        os.makedirs(TEST_NOTES_DIR)
        kb.notes = {} # Clear in-memory notes

    @classmethod
    def tearDownClass(cls):
        """Clean up the test directory after all tests."""
        if os.path.exists(TEST_NOTES_DIR):
            shutil.rmtree(TEST_NOTES_DIR)

    def test_get_daily_note(self):
        """Test retrieving the daily note via the API."""
        client = TestClient(app)
        response = client.get("/api/notes/daily")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        today_title = datetime.now().strftime("%Y-%m-%d")

        self.assertEqual(data["title"], today_title)
        self.assertIn(f"# Daily Note for {today_title}", data["content"])

        # Verify the note was created in the filesystem
        self.assertTrue(os.path.exists(os.path.join(TEST_NOTES_DIR, f"{today_title}.md")))

if __name__ == "__main__":
    unittest.main()