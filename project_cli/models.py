"""Object models for users, projects, and tasks."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Task:
    title: str
    description: str = ""
    completed: bool = False
    contributors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "contributors": self.contributors,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            completed=data.get("completed", False),
            contributors=data.get("contributors", []),
            created_at=data.get("created_at", datetime.now().isoformat(timespec="seconds")),
        )


@dataclass
class Project:
    title: str
    owner: str
    description: str = ""
    tasks: List[Task] = field(default_factory=list)

    def to_dict(self):
        return {
            "title": self.title,
            "owner": self.owner,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data["title"],
            owner=data["owner"],
            description=data.get("description", ""),
            tasks=[Task.from_dict(item) for item in data.get("tasks", [])],
        )


@dataclass
class User:
    name: str
    email: str = ""
    projects: List[Project] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "projects": [project.to_dict() for project in self.projects],
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            email=data.get("email", ""),
            projects=[Project.from_dict(item) for item in data.get("projects", [])],
        )
