"""JSON persistence and reusable application operations."""
import json
from pathlib import Path
from typing import List
from .models import User, Project, Task


class StorageError(Exception):
    """Raised when application data cannot be read or written."""


class ProjectManager:
    def __init__(self, data_file="data/projects.json"):
        self.data_file = Path(data_file)
        self.users: List[User] = []
        self.load()

    def load(self):
        if not self.data_file.exists():
            self.users = []
            return
        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                raw = json.load(file)
            self.users = [User.from_dict(item) for item in raw.get("users", [])]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise StorageError(f"Could not load data from {self.data_file}: {exc}") from exc

    def save(self):
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.data_file.with_suffix(self.data_file.suffix + ".tmp")
            with temporary.open("w", encoding="utf-8") as file:
                json.dump({"users": [user.to_dict() for user in self.users]}, file, indent=2)
            temporary.replace(self.data_file)
        except OSError as exc:
            raise StorageError(f"Could not save data to {self.data_file}: {exc}") from exc

    @staticmethod
    def _find_named(items, name, attribute="name"):
        return next((item for item in items if getattr(item, attribute).casefold() == name.casefold()), None)

    def add_user(self, name, email=""):
        if self._find_named(self.users, name):
            raise ValueError(f"User '{name}' already exists.")
        user = User(name=name.strip(), email=email.strip())
        if not user.name:
            raise ValueError("User name cannot be empty.")
        self.users.append(user)
        self.save()
        return user

    def list_users(self):
        return self.users

    def get_user(self, name):
        user = self._find_named(self.users, name)
        if user is None:
            raise ValueError(f"User '{name}' was not found.")
        return user

    def add_project(self, user_name, title, description=""):
        user = self.get_user(user_name)
        if not title.strip():
            raise ValueError("Project title cannot be empty.")
        if self._find_named(user.projects, title, "title"):
            raise ValueError(f"Project '{title}' already exists for {user.name}.")
        project = Project(title=title.strip(), owner=user.name, description=description.strip())
        user.projects.append(project)
        self.save()
        return project

    def list_projects(self, user_name=None):
        if user_name:
            return self.get_user(user_name).projects
        return [project for user in self.users for project in user.projects]

    def get_project(self, title):
        for user in self.users:
            project = self._find_named(user.projects, title, "title")
            if project:
                return project
        raise ValueError(f"Project '{title}' was not found.")

    def add_task(self, project_title, title, description="", contributors=None):
        project = self.get_project(project_title)
        if not title.strip():
            raise ValueError("Task title cannot be empty.")
        if self._find_named(project.tasks, title, "title"):
            raise ValueError(f"Task '{title}' already exists in project '{project.title}'.")
        contributor_names = []
        for name in contributors or []:
            user = self.get_user(name)
            if user.name not in contributor_names:
                contributor_names.append(user.name)
        task = Task(title=title.strip(), description=description.strip(), contributors=contributor_names)
        project.tasks.append(task)
        self.save()
        return task

    def list_tasks(self, project_title):
        return self.get_project(project_title).tasks

    def complete_task(self, project_title, task_title):
        project = self.get_project(project_title)
        task = self._find_named(project.tasks, task_title, "title")
        if task is None:
            raise ValueError(f"Task '{task_title}' was not found in project '{project.title}'.")
        task.completed = True
        self.save()
        return task

    def edit_project(self, title, new_title=None, description=None):
        project = self.get_project(title)
        if new_title and new_title.strip():
            other = self._find_named(
                [p for p in self.list_projects() if p is not project], new_title, "title"
            )
            if other:
                raise ValueError(f"Another project named '{new_title}' already exists.")
            project.title = new_title.strip()
        if description is not None:
            project.description = description.strip()
        self.save()
        return project

    def edit_task(self, project_title, task_title, new_title=None, description=None):
        project = self.get_project(project_title)
        task = self._find_named(project.tasks, task_title, "title")
        if task is None:
            raise ValueError(f"Task '{task_title}' was not found in project '{project.title}'.")
        if new_title and new_title.strip():
            other = self._find_named([t for t in project.tasks if t is not task], new_title, "title")
            if other:
                raise ValueError(f"Another task named '{new_title}' already exists in this project.")
            task.title = new_title.strip()
        if description is not None:
            task.description = description.strip()
        self.save()
        return task

    def search_projects(self, query):
        query = query.casefold()
        return [
            (user.name, project)
            for user in self.users
            for project in user.projects
            if query in project.title.casefold() or query in project.description.casefold()
        ]
