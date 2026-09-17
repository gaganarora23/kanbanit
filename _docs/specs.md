# Team Kanban Tool — MVP Specification

## 1. Product Goal

A simple Kanban board for small teams to manage shared work.

The MVP is frontend-first, uses a single board, one fixed/mock user context, and persists data in browser `localStorage`. There is no authentication or backend in the MVP.

## 2. MVP Scope

### Users and Roles

- Small-team use case.
- Roles:
  - **Admin**
  - **Member**
- Admin creates/manages users.
- Board access is limited to the owner and invited/created team members.
- MVP does not implement authentication.
- MVP uses a fixed/mock user context rather than real login.

### Board

- Exactly one board.
- The board represents the team's overall work.
- Fixed columns:
  1. Backlog
  2. To Do
  3. In Progress
  4. Done
- Columns cannot be renamed, reordered, added, or removed in the MVP.

### Cards

Cards represent individual tasks.

Each card has:

- Numeric incremental ID
- Title
- Description
- Assignee — exactly one person
- Priority — Low / Medium / High
- Labels
- Column/status
- Optional WIP-limit state derived from its current column

Card IDs are generated incrementally and remain stable even when the title changes.

### Card Operations

Board members can:

- Create cards
- Edit cards
- Drag cards between columns
- Assign cards
- Change priority
- Add/remove labels
- Delete cards

Card deletion requires confirmation.

Cards remain visible indefinitely after reaching **Done**.

There is no automatic archival.

### Labels

Initial system labels:

- Bug
- Feature
- Enhancement
- Documentation

The mock already supports adding labels, so users can create additional labels.

### WIP Limits

- WIP limits are optional and configured per column.
- If a column's WIP limit is exceeded:
  - The card move is still allowed.
  - The UI displays a clear visual warning.
- WIP limits do not block users from moving cards.

### Views

MVP has one primary view:

- Kanban board

No separate My Cards view, dashboard, reporting view, or activity view.

### Comments and History

Not included in MVP:

- Comments
- @mentions
- Attachments
- Activity log
- Audit history

### Due Dates and Notifications

Not included in MVP:

- Due dates
- Due times
- Reminders
- Notifications

## 3. Permissions

### Admin

Admin can:

- View board
- Create/edit/move/delete cards
- Manage users
- Manage labels
- Configure WIP limits

### Member

Members can:

- View board
- Create cards
- Edit cards
- Move cards
- Assign cards
- Change priority
- Manage card labels
- Delete cards

All board members have the same card-level permissions.

## 4. Persistence

MVP uses browser `localStorage`.

Requirements:

- Card creation persists across refreshes.
- Card edits persist across refreshes.
- Card movement persists across refreshes.
- User changes persist across refreshes.
- Label changes persist across refreshes.
- WIP-limit configuration persists across refreshes.
- Deleted cards remain deleted after refresh.

A reset-to-default capability should be available for development/demo purposes.

## 5. Initial Seed Data

The application should initialize with useful demo data rather than an empty board.

Seed data should include:

- A small set of mock team members.
- A small set of representative cards.
- Initial labels:
  - Bug
  - Feature
  - Enhancement
  - Documentation
- Sensible example priorities and assignments.
- Example cards distributed across the Kanban columns.

The exact seed content can follow the existing Lovable mock.

## 6. Data Model

### Board

```text
Board
- id
- name
- columns[]
- wipLimits{}
- labelIds[]
- memberIds[]
```

Because the MVP has exactly one board, the board ID can remain a fixed value.

### User

```text
User
- id
- name
- role: ADMIN | MEMBER
```

### Card

```text
Card
- id: number
- title: string
- description: string
- assigneeId: string
- priority: LOW | MEDIUM | HIGH
- labelIds: string[]
- columnId: BACKLOG | TODO | IN_PROGRESS | DONE
```

### Label

```text
Label
- id
- name
```

### WIP Limits

WIP limits can be represented as a mapping:

```text
wipLimits = {
  BACKLOG: null,
  TODO: 5,
  IN_PROGRESS: 3,
  DONE: null
}
```

`null` means there is no WIP limit.

## 7. Local Storage

Use a single application state object rather than scattering independent pieces of state across many storage keys.

Conceptually:

```text
kanbanState
├── board
├── users
├── cards
├── labels
└── settings
```

Persist the complete state whenever relevant state changes.

## 8. Card ID Generation

Card IDs are incremental integers.

Example:

```text
1001
1002
1003
1004
```

When creating a card:

1. Find the current highest card ID.
2. Increment it.
3. Assign the new number to the card.
4. Never reuse IDs from deleted cards.

This keeps IDs stable and avoids problems caused by using editable titles as identifiers.

## 9. Core User Flows

### Create Card

1. User selects Add Card.
2. User enters card information.
3. System assigns the next incremental numeric ID.
4. Card is added to the selected column.
5. State is persisted to localStorage.

### Move Card

1. User drags a card.
2. System updates its column.
3. If the destination column exceeds its WIP limit, the move still succeeds.
4. The column/card displays the WIP warning.
5. State is persisted.

### Edit Card

1. User opens a card.
2. User changes editable fields.
3. System saves changes.
4. State is persisted.

### Delete Card

1. User selects Delete.
2. Confirmation is displayed.
3. If confirmed, the card is removed.
4. State is persisted.

### Add Label

1. User opens label management.
2. User creates a label.
3. Label becomes available for cards.
4. State is persisted.

## 10. Non-Goals for MVP

Do not build:

- Authentication
- Authorization backed by a server
- FastAPI backend
- Database
- Real-time collaboration
- Multiple boards
- Projects
- Subtasks
- Epics
- Comments
- Attachments
- Notifications
- Due dates
- Activity/audit history
- Reporting/analytics
- My Cards view
- Automated card movement
- Workflow automation
- External integrations
- Email notifications

## 11. Future Architecture Direction

Although the MVP uses localStorage, the frontend state model should be structured so a future backend can replace local persistence without requiring a major UI rewrite.

Future architecture:

```text
Current MVP

React/UI
   ↓
State Management
   ↓
localStorage


Future

React/UI
   ↓
State Management
   ↓
API Client
   ↓
FastAPI
   ↓
Database
```

The UI should therefore avoid coupling components directly to `localStorage`. Use a small persistence/service layer so that localStorage can later be replaced by API calls.

## 12. MVP Success Criteria

The MVP is complete when a small team can:

1. Open the board.
2. See team members and existing work.
3. Create a task.
4. Assign it to one team member.
5. Set priority.
6. Add labels.
7. Move the task through the four Kanban columns.
8. See WIP warnings when limits are exceeded.
9. Edit a task.
10. Delete a task with confirmation.
11. Refresh the browser without losing changes.
12. Manage labels and WIP limits as an admin.

## 13. Product Principle

Keep the MVP intentionally simple.

The core loop is:

**Create → Assign → Prioritize → Move → Complete**

Avoid adding collaboration, automation, reporting, or workflow complexity until the basic Kanban experience is working well.
