import json
import tempfile
import unittest
from pathlib import Path

from project_cli.storage import ProjectManager


class ProjectManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "projects.json"
        self.manager = ProjectManager(self.data_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_user_and_prevent_duplicate(self):
        self.manager.add_user("Alex")
        self.assertEqual(len(self.manager.list_users()), 1)
        with self.assertRaises(ValueError):
            self.manager.add_user("alex")

    def test_project_and_task_relationships(self):
        self.manager.add_user("Alex")
        self.manager.add_user("Sam")
        self.manager.add_project("Alex", "CLI Tool", "Build a tracker")
        task = self.manager.add_task("CLI Tool", "Implement add-task", contributors=["Sam", "Alex"])
        self.assertEqual(task.contributors, ["Sam", "Alex"])
        self.assertEqual(len(self.manager.list_tasks("CLI Tool")), 1)

    def test_completion_is_persisted(self):
        self.manager.add_user("Alex")
        self.manager.add_project("Alex", "CLI Tool")
        self.manager.add_task("CLI Tool", "Write tests")
        self.manager.complete_task("CLI Tool", "Write tests")
        reloaded = ProjectManager(self.data_file)
        self.assertTrue(reloaded.list_tasks("CLI Tool")[0].completed)

    def test_search_projects(self):
        self.manager.add_user("Alex")
        self.manager.add_project("Alex", "CLI Tool", "A project tracker")
        self.assertEqual(len(self.manager.search_projects("tracker")), 1)
        self.assertEqual(len(self.manager.search_projects("missing")), 0)

    def test_json_file_is_created(self):
        self.manager.add_user("Alex")
        self.assertTrue(self.data_file.exists())
        payload = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["users"][0]["name"], "Alex")


if __name__ == "__main__":
    unittest.main()
