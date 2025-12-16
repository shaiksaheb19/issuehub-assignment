from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SqlEnum,
    Text,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base   # <-- Make sure this is correct


# ============================
# ENUMS
# ============================
class RoleEnum(str, Enum):
    viewer = "viewer"
    developer = "developer"
    manager = "manager"


class IssueStatusEnum(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


# ============================
# MODELS
# ============================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")
    memberships = relationship("ProjectMember", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)  # <-- add this

    owner = relationship("User", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project")
    issues = relationship("Issue", back_populates="project")


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(SqlEnum(RoleEnum), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="memberships")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(SqlEnum(IssueStatusEnum), default=IssueStatusEnum.open)
    priority = Column(SqlEnum(PriorityEnum), default=PriorityEnum.medium)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)  # <-- add this

    project = relationship("Project", back_populates="issues")
    assignee = relationship("User", foreign_keys=[assignee_id])
    reporter = relationship("User", foreign_keys=[reporter_id])
    comments = relationship("Comment", back_populates="issue")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    author_id = Column(Integer, ForeignKey("users.id"))  # renamed from user_id

    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="comments")
    user = relationship("User", foreign_keys=[author_id])
