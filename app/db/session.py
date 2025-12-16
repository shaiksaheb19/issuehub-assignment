from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# sqlite local dev; for Postgres, set DATABASE_URL in .env
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that yields a DB session and makes sure it's closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
