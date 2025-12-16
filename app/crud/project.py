from sqlalchemy.orm import Session
from app.db import models
from app.schemas.pydantic_schemas import ProjectCreate


def create_project(db: Session, project_in: ProjectCreate, owner_id: int):
    project = models.Project(
        name=project_in.name,
        key=project_in.key,
        description=project_in.description,
        owner_id=owner_id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project



def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()


def get_project_by_key(db: Session, key: str):
    return db.query(models.Project).filter(models.Project.key == key).first()
