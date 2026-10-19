"""Command-line interface built with argparse."""
import argparse
import sys
from rich import print  # External package: adds readable terminal output.
from .storage import ProjectManager, StorageError


def build_parser():
    parser = argparse.ArgumentParser(
        prog="project-cli",
        description="Manage team users, projects, and tasks."
    )
    parser.add_argument("--data", default="data/projects.json",
                        help="path to JSON data file (default: data/projects.json)")
    commands = parser.add_subparsers(dest="command", required=True)

    p = commands.add_parser("add-user", help="create a user")
    p.add_argument("--name", required=True)
    p.add_argument("--email", default="")

    commands.add_parser("list-users", help="list all users")

    p = commands.add_parser("add-project", help="create a project for a user")
    p.add_argument("--user", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")

    p = commands.add_parser("list-projects", help="list projects")
    p.add_argument("--user", help="show projects belonging to this user")

    p = commands.add_parser("search-projects", help="search project titles and descriptions")
    p.add_argument("--query", required=True)

    p = commands.add_parser("add-task", help="add a task to a project")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--contributors", nargs="*", default=[],
                   help="one or more existing user names")

    p = commands.add_parser("list-tasks", help="list tasks in a project")
    p.add_argument("--project", required=True)

    p = commands.add_parser("complete-task", help="mark a task as complete")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True)

    p = commands.add_parser("edit-project", help="edit a project's title or description")
    p.add_argument("--title", required=True, help="current project title")
    p.add_argument("--new-title")
    p.add_argument("--description")

    p = commands.add_parser("edit-task", help="edit a task's title or description")
    p.add_argument("--project", required=True)
    p.add_argument("--title", required=True, help="current task title")
    p.add_argument("--new-title")
    p.add_argument("--description")
    return parser


def _print_projects(projects):
    if not projects:
        print("No projects found.")
        return
    for project in projects:
        print(f"- {project.title} (owner: {project.owner})")
        if project.description:
            print(f"  Description: {project.description}")
        print(f"  Tasks: {len(project.tasks)}")


def _print_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        status = "DONE" if task.completed else "TODO"
        contributors = ", ".join(task.contributors) if task.contributors else "None"
        print(f"- [{status}] {task.title}")
        if task.description:
            print(f"  Description: {task.description}")
        print(f"  Contributors: {contributors}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        manager = ProjectManager(args.data)
        if args.command == "add-user":
            user = manager.add_user(args.name, args.email)
            print(f"Created user: {user.name}")
        elif args.command == "list-users":
            if not manager.list_users():
                print("No users found.")
            for user in manager.list_users():
                print(f"- {user.name}" + (f" <{user.email}>" if user.email else ""))
        elif args.command == "add-project":
            project = manager.add_project(args.user, args.title, args.description)
            print(f"Created project '{project.title}' for {project.owner}.")
        elif args.command == "list-projects":
            _print_projects(manager.list_projects(args.user))
        elif args.command == "search-projects":
            results = manager.search_projects(args.query)
            if not results:
                print("No matching projects found.")
            for owner, project in results:
                print(f"- {project.title} (owner: {owner})")
        elif args.command == "add-task":
            task = manager.add_task(args.project, args.title, args.description, args.contributors)
            print(f"Created task '{task.title}' in project '{args.project}'.")
        elif args.command == "list-tasks":
            _print_tasks(manager.list_tasks(args.project))
        elif args.command == "complete-task":
            task = manager.complete_task(args.project, args.title)
            print(f"Marked task '{task.title}' as complete.")
        elif args.command == "edit-project":
            project = manager.edit_project(args.title, args.new_title, args.description)
            print(f"Updated project: {project.title}")
        elif args.command == "edit-task":
            task = manager.edit_task(args.project, args.title, args.new_title, args.description)
            print(f"Updated task: {task.title}")
        return 0
    except (ValueError, StorageError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
