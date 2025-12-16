# app/api/project_members.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas import pydantic_schemas as schemas
from app.db import models
from app.crud import crud

router = APIRouter(prefix="/api/projects", tags=["project_members"])


@router.post("/{project_id}/members", response_model=schemas.ProjectMemberOut)
def add_member(
    project_id: int,
    member_in: schemas.ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # ensure project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # only existing project members can add another member
    current_member = crud.get_project_member(db, project_id, current_user.id)
    if not current_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )

    # look up user by email from payload
    user = crud.get_user_by_email(db, member_in.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # create project member row
    pm = models.ProjectMember(
        project_id=project_id,
        user_id=user.id,
        role=member_in.role,
    )
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


@router.get("/{project_id}/members", response_model=List[schemas.ProjectMemberOut])
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # ensure current user is at least a member
    member = crud.get_project_member(db, project_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this project",
        )

    # return all members for this project
    members = (
        db.query(models.ProjectMember)
        .filter(models.ProjectMember.project_id == project_id)
        .all()
    )
    return members
