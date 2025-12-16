from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas import pydantic_schemas as schemas
from app.crud import crud
from app.db import models

router = APIRouter(prefix="/api/issues", tags=["comments"])


@router.get("/{issue_id}/comments", response_model=List[schemas.CommentOut])
def list_comments(
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

    return crud.get_comments_for_issue(db, issue_id)


@router.post("/{issue_id}/comments", response_model=schemas.CommentOut)
def create_comment(
    issue_id: int,
    payload: schemas.CommentCreate,
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

    comment = crud.create_comment(
        db, issue_id=issue_id, author_id=current_user.id, body=payload.body
    )
    return comment
