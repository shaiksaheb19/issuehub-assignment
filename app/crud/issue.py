from sqlalchemy.orm import Session
from app.db import models
from app.schemas.pydantic_schemas import IssueCreate


def create_issue(db: Session, issue_in: IssueCreate):
    issue = models.Issue(
        project_id=issue_in.project_id,
        title=issue_in.title,
        description=issue_in.description,
        status=issue_in.status,
        priority=issue_in.priority,
        reporter_id=issue_in.reporter_id,
        assignee_id=issue_in.assignee_id
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


def get_issue(db: Session, issue_id: int):
    return db.query(models.Issue).filter(models.Issue.id == issue_id).first()


def list_issues(db: Session, project_id: int):
    return db.query(models.Issue).filter(
        models.Issue.project_id == project_id
    ).all()
