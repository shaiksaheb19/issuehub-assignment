from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

# Import enums from DB models
from app.db.models import RoleEnum, IssueStatusEnum, PriorityEnum

# -------------------- AUTH SCHEMAS --------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# -------------------- USER SCHEMAS --------------------

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# -------------------- PROJECT SCHEMAS --------------------

class ProjectCreate(BaseModel):
    name: str
    key: str
    description: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    key: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# -------------------- PROJECT MEMBER SCHEMAS --------------------

class ProjectMemberCreate(BaseModel):
    email: EmailStr
    role: RoleEnum


class ProjectMemberOut(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: RoleEnum
    joined_at: datetime

    model_config = {"from_attributes": True}


# -------------------- ISSUE SCHEMAS --------------------

class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityEnum
    assignee_id: Optional[int] = None


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assignee_id: Optional[int] = None


class IssueOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: IssueStatusEnum
    priority: PriorityEnum
    reporter_id: int
    assignee_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# -------------------- COMMENT SCHEMAS --------------------

class CommentCreate(BaseModel):
    body: str


class CommentOut(BaseModel):
    id: int
    issue_id: int
    author_id: int
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
