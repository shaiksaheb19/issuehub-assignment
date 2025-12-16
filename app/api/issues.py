from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas import pydantic_schemas as schemas
from app.crud import crud
from app.db import models

router = APIRouter(prefix="/api", tags=["issues"])  # base /api


@router.post("/projects/{project_id}/issues", response_model=schemas.IssueOut)
def create_issue(
    project_id: int,
    issue_in: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # must be project member
    member = crud.get_project_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )

    issue = crud.create_issue(db, project_id, issue_in, reporter_id=current_user.id)
    return issue


@router.get("/projects/{project_id}/issues", response_model=List[schemas.IssueOut])
def list_issues(
    project_id: int,
    q: Optional[str] = None,
    status_filter: Optional[str] = None,   # renamed
    priority: Optional[str] = None,
    assignee: Optional[int] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    member = crud.get_project_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )

    issues = crud.get_issues(
        db,
        project_id,
        q=q,
        status=status_filter,  # pass renamed variable
        priority=priority,
        assignee=assignee,
        sort=sort,
    )
    return issues


@router.get("/issues/{issue_id}", response_model=schemas.IssueOut)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = crud.get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    member = crud.get_project_member(db, issue.project_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )

    return issue


@router.patch("/issues/{issue_id}", response_model=schemas.IssueOut)
def patch_issue(
    issue_id: int,
    issue_updates: schemas.IssueUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = crud.get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    member = crud.get_project_member(db, issue.project_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )

    updates = issue_updates.dict(exclude_unset=True)

    # If changing status / assignee / priority, require manager
    if any(field in updates for field in ("status", "assignee_id", "priority")):
        if not crud.is_project_manager(db, issue.project_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only project managers can change status, "
                    "assignee, or priority"
                ),
            )

    updated = crud.update_issue(db, issue, updates)
    return updated


@router.delete("/issues/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = crud.get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    member = crud.get_project_member(db, issue.project_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )

    crud.delete_issue(db, issue)
    return {"status": "deleted"}
