from typing import Literal, Optional

from pydantic import BaseModel, Field

Status = Literal["parked", "todo", "in_progress", "complete"]
Priority = Literal["P1", "P2", "P3", "P4"]


class Project(BaseModel):
    id: str
    name: str
    color: str


class ProjectCreate(BaseModel):
    name: str
    color: str


class Task(BaseModel):
    id: str
    projectId: str
    title: str
    description: Optional[str] = None
    status: Status
    priority: Optional[Priority] = None
    labelIds: list[str] = Field(default_factory=list)
    assigneeId: Optional[str] = None
    due: Optional[str] = None
    createdAt: str


class TaskCreate(BaseModel):
    projectId: str
    title: str
    description: Optional[str] = None
    status: Status
    priority: Optional[Priority] = None
    labelIds: list[str] = Field(default_factory=list)
    assigneeId: Optional[str] = None
    due: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    labelIds: Optional[list[str]] = None
    assigneeId: Optional[str] = None
    due: Optional[str] = None


class TaskMove(BaseModel):
    status: Status
    beforeTaskId: Optional[str] = None


class Label(BaseModel):
    id: str
    name: str
    color: str


class LabelCreate(BaseModel):
    name: str
    color: str


class Member(BaseModel):
    id: str
    name: str
    initials: str
    color: str
    isYou: bool = False


class MemberCreate(BaseModel):
    name: str


# ---- Auth ----


class User(BaseModel):
    """A login credential holder. Distinct from Member (the team member shown on task
    cards) — a User authenticates; a Member is just a display identity on the board."""

    id: str
    username: str
    hashed_password: str


class UserPublic(BaseModel):
    id: str
    username: str


class RegisterRequest(BaseModel):
    username: str
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
