from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError  # NEW

from app.db import models
from app.schemas import pydantic_schemas as schemas
from app.core.security import hash_password


# --- User CRUD ---
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).get(user_id)


def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    user = models.User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- Project membership helpers ---
def get_project_member(
    db: Session, project_id: int, user_id: int
) -> Optional[models.ProjectMember]:
    return (
        db.query(models.ProjectMember)
        .filter(
            models.ProjectMember.project_id == project_id,
            models.ProjectMember.user_id == user_id,
        )
        .first()
    )


def is_project_manager(db: Session, project_id: int, user_id: int) -> bool:
    member = get_project_member(db, project_id, user_id)
    return member is not None and member.role == models.RoleEnum.manager


# --- Project CRUD ---
def create_project(
    db: Session, project_in: schemas.ProjectCreate, owner_id: int
) -> models.Project:
    project = models.Project(
        name=project_in.name,
        key=project_in.key,
        description=project_in.description,
        owner_id=owner_id,
    )
    db.add(project)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # key must be unique
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this key already exists",
        )
    db.refresh(project)

    # add owner as manager/maintainer
    pm = models.ProjectMember(
        project_id=project.id,
        user_id=owner_id,
        role=models.RoleEnum.manager,
    )
    db.add(pm)
    db.commit()
    db.refresh(pm)

    return project


def get_projects_for_user(db: Session, user_id: int) -> List[models.Project]:
    return (
        db.query(models.Project)
        .join(models.ProjectMember)
        .filter(models.ProjectMember.user_id == user_id)
        .all()
    )


def add_project_member(db: Session, project_id: int, email: str, role: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise ValueError("User not found")

    pm = models.ProjectMember(project_id=project_id, user_id=user.id, role=role)
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


# --- Issue CRUD ---
def create_issue(
    db: Session, project_id: int, issue_in: schemas.IssueCreate, reporter_id: int
) -> models.Issue:
    issue = models.Issue(
        project_id=project_id,
        title=issue_in.title,
        description=issue_in.description,
        priority=issue_in.priority,
        reporter_id=reporter_id,
        assignee_id=issue_in.assignee_id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def get_issues(
    db: Session,
    project_id: int,
    q: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee: Optional[int] = None,
    sort: Optional[str] = None,
):
    query = db.query(models.Issue).filter(models.Issue.project_id == project_id)
    if q:
        query = query.filter(
            (models.Issue.title.ilike(f"%{q}%"))
            | (models.Issue.description.ilike(f"%{q}%"))
        )
    if status:
        query = query.filter(models.Issue.status == status)
    if priority:
        query = query.filter(models.Issue.priority == priority)
    if assignee:
        query = query.filter(models.Issue.assignee_id == assignee)
    if sort == "created_at":
        query = query.order_by(models.Issue.created_at.desc())
    elif sort == "priority":
        query = query.order_by(models.Issue.priority)
    return query.all()


def get_issue(db: Session, issue_id: int) -> Optional[models.Issue]:
    return db.query(models.Issue).filter(models.Issue.id == issue_id).first()


def update_issue(
    db: Session, issue: models.Issue, updates: Dict[str, Any]
) -> models.Issue:
    for k, v in updates.items():
        if hasattr(issue, k) and v is not None:
            setattr(issue, k, v)
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def delete_issue(db: Session, issue: models.Issue) -> None:
    db.delete(issue)
    db.commit()


# --- Comments ---
def create_comment(
    db: Session, issue_id: int, author_id: int, body: str
) -> models.Comment:
    comment = models.Comment(issue_id=issue_id, author_id=author_id, body=body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comments_for_issue(db: Session, issue_id: int):
    return (
        db.query(models.Comment)
        .filter(models.Comment.issue_id == issue_id)
        .order_by(models.Comment.created_at.asc())
        .all()
    )
