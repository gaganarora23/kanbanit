# Kanvas — Kanban Tool Specification

> Supersedes the earlier single-board MVP spec. The frontend (`gaganarora23/lovable-tasks`,
> local working copy at `frontend/`) was generated with Lovable as "Kanvas — Mini Kanban Board"
> and already implements the model below, including a mock API contract
> (`frontend/mock-api/`) meant to be backed by this repo's FastAPI backend. This spec documents
> that model so the backend can be built to match it.

## 1. Product Goal

A lightweight, multi-project kanban board for a small team to track work across several
projects at once.

The frontend keeps state in memory + `localStorage` today. The mock API contract in
`frontend/mock-api/` (OpenAPI spec + seed data) defines the shape the FastAPI backend should
implement so the frontend's store (`src/lib/kanban/store.tsx`) can be pointed at real `fetch()`
calls with no component changes.

## 2. Scope

### Users and Roles

- Small-team use case, no authentication in this phase.
- A fixed set of team members (seed: You, Marc O., Lena V.), one of them flagged `isYou`.
- No Admin/Member distinction and no per-user permissions — any team member can perform any
  action.

### Projects

- Multiple projects exist side by side (seed: Atlas Redesign, Mobile App, Design System,
  Marketing Site).
- Each project has an id, name, and color, and owns its own set of tasks.
- The sidebar lists all projects with an open-task count; selecting one shows its board.

### Board / Columns

Each project's board has four fixed columns, identified by `status`:

1. `parked` — "Parked / Backlog"
2. `todo` — "To Do"
3. `in_progress` — "In Progress"
4. `complete` — "Complete"

Columns are not renameable, reorderable, addable, or removable.

### Tasks

Each task has:

- `id` (string)
- `projectId` — the project it belongs to
- `title`
- `description` (optional)
- `status` — one of `parked` / `todo` / `in_progress` / `complete`
- `priority` — one of `P1` (urgent) / `P2` (high) / `P3` (medium) / `P4` (low), or `null`
- `labelIds` — zero or more labels
- `assigneeId` — exactly one member, or `null` (unassigned)
- `due` (optional, free-form string, e.g. "Today", "Mon", "2w", "60%")
- `createdAt` (ISO-8601 timestamp)

### Task Operations

Team members can:

- Create a task (inline "Add a task to `<column>`..." input, or the "+ New task" button)
- Edit a task's title, description, priority, labels, and assignee
- Move a task between columns via drag-and-drop, or reorder it within a column
- Delete a task

There is no WIP-limit concept and no confirmation step is required for deletion in the current
frontend implementation.

### Labels

Seed labels: Bug, Feature, Research, Content, Mobile, API, Ideas, Shipped — each with a name and
color. New labels can be created (name + color) and attached to tasks.

### Views

- One primary view per project: its kanban board.
- Switching projects via the sidebar is the only navigation.

## 3. Data Model

```text
Project
- id: string
- name: string
- color: string        # hex

Task
- id: string
- projectId: string
- title: string
- description?: string
- status: parked | todo | in_progress | complete
- priority: P1 | P2 | P3 | P4 | null
- labelIds: string[]
- assigneeId: string | null
- due?: string
- createdAt: string     # ISO-8601

Label
- id: string
- name: string
- color: string         # hex

Member
- id: string
- name: string
- initials: string
- color: string          # hex
- isYou?: boolean
```

## 4. Persistence

Today: browser `localStorage`, keyed `kanvas-board-state-v1`, holding projects/tasks/labels/
members as one object. Survives refresh.

Future: replace the store's in-memory/localStorage actions with calls to the API described
below, backed by this repo's FastAPI + PostgreSQL backend. The component layer should not need
to change.

## 5. API Contract (for the backend to implement)

Full contract: `frontend/mock-api/openapi.yaml`. Seed data matching it: `frontend/mock-api/db.json`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/projects` | List projects |
| POST | `/projects` | Create a project |
| GET | `/projects/{projectId}/tasks` | List a project's tasks |
| POST | `/tasks` | Create a task |
| PATCH | `/tasks/{taskId}` | Update a task |
| DELETE | `/tasks/{taskId}` | Delete a task |
| POST | `/tasks/{taskId}/move` | Move a task to a column, optionally before another task |
| GET | `/labels` | List labels |
| POST | `/labels` | Create a label |
| GET | `/members` | List members |
| POST | `/members` | Create a member |

`POST /tasks/{taskId}/move` takes `{ status, beforeTaskId? }` — moves the task to `status`, and
positions it immediately before `beforeTaskId` within that column, or appends to the end if
`beforeTaskId` is omitted.

## 6. Non-Goals (current phase)

- Authentication / authorization
- Admin vs. Member roles or any per-user permissions
- WIP limits
- Comments, @mentions, attachments, activity/audit log
- Due dates as real dates/times, reminders, notifications
- Real-time collaboration
- Reporting/analytics, a "My Tasks" view

## 7. Success Criteria

The current phase is complete when a small team can, per project:

1. See all projects and their open-task counts in the sidebar.
2. Open a project's board and see its tasks distributed across the four columns.
3. Create a task via the inline column input or the "New task" button.
4. Assign it to a team member, set its priority, and attach labels.
5. Drag it between columns, and reorder it within a column.
6. Edit a task's details.
7. Delete a task.
8. Refresh the browser without losing any changes.
9. Create a new label on the fly.

## 8. Product Principle

Keep the board fast and low-friction: inline task creation, drag-and-drop, no required fields
beyond a title. Defer roles, WIP limits, and other process controls until there's a concrete
need for them.
