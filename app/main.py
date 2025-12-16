# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import models
from app.db.session import engine

# import routers
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.issues import router as issues_router
from app.api.project_members import router as members_router
from app.api.comments import router as comments_router

# ensure tables exist for dev
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="IssueHub Backend")

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(issues_router)
app.include_router(members_router)
app.include_router(comments_router)


@app.get("/")
def root():
    return {"message": "IssueHub is running"}
