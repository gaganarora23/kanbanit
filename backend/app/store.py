"""In-memory mock database.

This is a stand-in for a real database (e.g. Postgres) that will replace it later. Route
handlers only talk to this repository layer, never to the underlying dicts directly, so
swapping the storage backend later shouldn't require route changes.
"""

from datetime import datetime, timezone
from itertools import count
from typing import Optional

from app.auth import generate_token, hash_password
from app.models import Label, LabelCreate, Member, MemberCreate, Project, ProjectCreate, Task, TaskCreate, TaskMove, TaskUpdate, User
from app.seed import DEMO_USERNAME, DEMO_PASSWORD, SEED_LABELS, SEED_MEMBERS, SEED_PROJECTS, SEED_TASKS

COLUMN_ORDER = ["parked", "todo", "in_progress", "complete"]


class NotFoundError(Exception):
    def __init__(self, resource: str, resource_id: str):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} '{resource_id}' not found")


class InMemoryStore:
    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._tasks: dict[str, Task] = {}
        self._labels: dict[str, Label] = {}
        self._members: dict[str, Member] = {}
        # (projectId, status) -> ordered list of task ids, defines column position
        self._column_order: dict[tuple[str, str], list[str]] = {}
        self._users: dict[str, User] = {}
        self._users_by_username: dict[str, str] = {}  # username -> user id
        self._tokens: dict[str, str] = {}  # token -> user id
        self._id_counter = count(1)
        self._seed()

    def _seed(self) -> None:
        for p in SEED_PROJECTS:
            self._projects[p["id"]] = Project(**p)
        for t in SEED_TASKS:
            task = Task(**t)
            self._tasks[task.id] = task
            self._column_order.setdefault((task.projectId, task.status), []).append(task.id)
        for l in SEED_LABELS:
            self._labels[l["id"]] = Label(**l)
        for m in SEED_MEMBERS:
            self._members[m["id"]] = Member(**m)
        demo_user = User(
            id="u-demo",
            username=DEMO_USERNAME,
            hashed_password=hash_password(DEMO_PASSWORD),
        )
        self._users[demo_user.id] = demo_user
        self._users_by_username[demo_user.username] = demo_user.id

    def _next_id(self, prefix: str) -> str:
        return f"{prefix}-{next(self._id_counter)}-{int(datetime.now(timezone.utc).timestamp() * 1000)}"

    # ---- Projects ----

    def list_projects(self) -> list[Project]:
        return list(self._projects.values())

    def get_project(self, project_id: str) -> Project:
        try:
            return self._projects[project_id]
        except KeyError:
            raise NotFoundError("Project", project_id) from None

    def create_project(self, data: ProjectCreate) -> Project:
        project = Project(id=self._next_id("p"), name=data.name, color=data.color)
        self._projects[project.id] = project
        return project

    # ---- Tasks ----

    def list_tasks_by_project(self, project_id: str) -> list[Task]:
        self.get_project(project_id)  # raises NotFoundError if missing
        ordered: list[Task] = []
        for status in COLUMN_ORDER:
            for task_id in self._column_order.get((project_id, status), []):
                ordered.append(self._tasks[task_id])
        return ordered

    def get_task(self, task_id: str) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError:
            raise NotFoundError("Task", task_id) from None

    def create_task(self, data: TaskCreate) -> Task:
        self.get_project(data.projectId)  # raises NotFoundError if missing
        task = Task(
            id=self._next_id("t"),
            projectId=data.projectId,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            labelIds=list(data.labelIds),
            assigneeId=data.assigneeId,
            due=data.due,
            createdAt=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        self._tasks[task.id] = task
        self._column_order.setdefault((task.projectId, task.status), []).append(task.id)
        return task

    def update_task(self, task_id: str, data: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        updates = data.model_dump(exclude_unset=True)

        new_status = updates.pop("status", None)
        updated = task.model_copy(update=updates)

        if new_status is not None and new_status != task.status:
            self._remove_from_column(task.projectId, task.status, task.id)
            updated = updated.model_copy(update={"status": new_status})
            self._column_order.setdefault((updated.projectId, new_status), []).append(updated.id)

        self._tasks[task_id] = updated
        return updated

    def delete_task(self, task_id: str) -> None:
        task = self.get_task(task_id)
        self._remove_from_column(task.projectId, task.status, task.id)
        del self._tasks[task_id]

    def move_task(self, task_id: str, move: TaskMove) -> Task:
        task = self.get_task(task_id)

        if move.beforeTaskId is not None:
            before_task = self.get_task(move.beforeTaskId)
            if before_task.projectId != task.projectId:
                raise NotFoundError("Task", move.beforeTaskId)

        self._remove_from_column(task.projectId, task.status, task.id)

        target_key = (task.projectId, move.status)
        column = self._column_order.setdefault(target_key, [])
        if move.beforeTaskId is not None and move.beforeTaskId in column:
            insert_at = column.index(move.beforeTaskId)
            column.insert(insert_at, task.id)
        else:
            column.append(task.id)

        updated = task.model_copy(update={"status": move.status})
        self._tasks[task_id] = updated
        return updated

    def _remove_from_column(self, project_id: str, status: str, task_id: str) -> None:
        column = self._column_order.get((project_id, status))
        if column and task_id in column:
            column.remove(task_id)

    # ---- Labels ----

    def list_labels(self) -> list[Label]:
        return list(self._labels.values())

    def create_label(self, data: LabelCreate) -> Label:
        label = Label(id=self._next_id("l"), name=data.name, color=data.color)
        self._labels[label.id] = label
        return label

    # ---- Members ----

    def list_members(self) -> list[Member]:
        return list(self._members.values())

    def create_member(self, data: MemberCreate) -> Member:
        initials = "".join(part[0].upper() for part in data.name.split() if part)[:2] or "?"
        member = Member(id=self._next_id("m"), name=data.name, initials=initials, color="#6b6b66")
        self._members[member.id] = member
        return member

    # ---- Users / auth ----

    def get_user_by_username(self, username: str) -> Optional[User]:
        user_id = self._users_by_username.get(username)
        return self._users.get(user_id) if user_id else None

    def create_user(self, username: str, hashed_password: str) -> User:
        if username in self._users_by_username:
            raise ValueError(f"username '{username}' already registered")
        user = User(id=self._next_id("u"), username=username, hashed_password=hashed_password)
        self._users[user.id] = user
        self._users_by_username[username] = user.id
        return user

    def create_token(self, user_id: str) -> str:
        token = generate_token()
        self._tokens[token] = user_id
        return token

    def get_user_by_token(self, token: str) -> Optional[User]:
        user_id = self._tokens.get(token)
        return self._users.get(user_id) if user_id else None
