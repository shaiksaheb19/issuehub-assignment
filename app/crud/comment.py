from sqlalchemy.orm import Session
from app.db import models
from app.schemas.pydantic_schemas import CommentCreate


def create_comment(db: Session, comment_in: CommentCreate):
    comment = models.Comment(
        issue_id=comment_in.issue_id,
        author_id=comment_in.author_id,
        body=comment_in.body
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, issue_id: int):
    return db.query(models.Comment).filter(
        models.Comment.issue_id == issue_id
    ).all()
