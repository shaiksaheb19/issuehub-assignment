from sqlalchemy.orm import Session
from app.db import models


def add_member(db: Session, project_id: int, user_id: int, role: str):
    member = models.ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_members(db: Session, project_id: int):
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id
    ).all()
