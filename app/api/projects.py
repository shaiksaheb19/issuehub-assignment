from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.schemas import pydantic_schemas as schemas
from app.crud import crud
from app.db import models

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("/", response_model=schemas.ProjectOut)
def create_project(
    project_in: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_project(db, project_in, owner_id=current_user.id)


@router.get("/", response_model=List[schemas.ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_projects_for_user(db, current_user.id)


@router.post("/{project_id}/members", response_model=schemas.ProjectMemberOut)
def add_member(
    project_id: int,
    payload: schemas.ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Only project managers can add members
    if not crud.is_project_manager(db, project_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project managers can add members",
        )

    try:
        member = crud.add_project_member(db, project_id, payload.email, payload.role)
    except ValueError:
        raise HTTPException(status_code=404, detail="User not found")
    return member
