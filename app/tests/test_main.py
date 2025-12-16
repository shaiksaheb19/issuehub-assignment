from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db


# --- Test DB setup (in-memory SQLite, fresh per test run) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def create_user_and_get_token(
    email: str = "alice@example.com", password: str = "secret"
):
    # signup – accept already-registered as OK
    resp = client.post(
        "/auth/signup",
        json={"name": email.split("@")[0], "email": email, "password": password},
    )
    assert resp.status_code in (200, 400)

    # login
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return token


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_root_works():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "IssueHub is running"


def test_auth_and_project_issue_comment_flow():
    # user A
    token_a = create_user_and_get_token("alice@example.com", "secret")
    headers_a = auth_headers(token_a)

    # create project with a unique key for this test
    resp = client.post(
        "/api/projects/",
        json={
            "name": "Test Project",
            "key": "TP1_flow",  # unique key
            "description": "Test project for API tests",
        },
        headers=headers_a,
    )
    # accept both first-time create (200) and duplicate key (400)
    assert resp.status_code in (200, 400)

    if resp.status_code == 200:
        project = resp.json()
    else:
        # if 400, fetch existing project from list
        resp_list = client.get("/api/projects/", headers=headers_a)
        assert resp_list.status_code == 200
        projects = resp_list.json()
        project = next(
            p for p in projects if p["key"] == "TP1_flow"
        )

    project_id = project["id"]
    ...


    # list projects for A
    resp = client.get("/api/projects/", headers=headers_a)
    assert resp.status_code == 200
    assert any(p["id"] == project_id for p in resp.json())

    # create issue
    resp = client.post(
        f"/api/projects/{project_id}/issues",
        json={
            "title": "First issue",
            "description": "Something is broken",
            "priority": "medium",
            "assignee_id": None,
        },
        headers=headers_a,
    )
    assert resp.status_code == 200
    issue = resp.json()
    issue_id = issue["id"]
    assert issue["project_id"] == project_id

    # add comment
    resp = client.post(
        f"/api/issues/{issue_id}/comments",
        json={"body": "Looking into this"},
        headers=headers_a,
    )
    assert resp.status_code == 200
    comment = resp.json()
    assert comment["issue_id"] == issue_id

    # list comments
    resp = client.get(f"/api/issues/{issue_id}/comments", headers=headers_a)
    assert resp.status_code == 200
    comments = resp.json()
    assert len(comments) >= 1
    assert any(c["id"] == comment["id"] for c in comments)


def test_project_membership_and_roles():
    # user A (manager)
    token_a = create_user_and_get_token("manager@example.com", "secret")
    headers_a = auth_headers(token_a)

    # create project by A with a different unique key
    resp = client.post(
        "/api/projects/",
        json={
            "name": "RBAC Project",
            "key": "RB1_rbac",  # unique key
            "description": "Role test",
        },
        headers=headers_a,
    )
    assert resp.status_code in (200, 400)

    if resp.status_code == 200:
        project = resp.json()
    else:
        resp_list = client.get("/api/projects/", headers=headers_a)
        assert resp_list.status_code == 200
        projects = resp_list.json()
        project = next(
            p for p in projects if p["key"] == "RB1_rbac"
        )

    project_id = project["id"]
    ...


    # user B (not member yet)
    token_b = create_user_and_get_token("bob@example.com", "secret")
    headers_b = auth_headers(token_b)

    # B should not see issues of this project
    resp = client.get(f"/api/projects/{project_id}/issues", headers=headers_b)
    assert resp.status_code == 403

    # A creates an issue
    resp = client.post(
        f"/api/projects/{project_id}/issues",
        json={
            "title": "RBAC issue",
            "description": "Test membership",
            "priority": "low",
            "assignee_id": None,
        },
        headers=headers_a,
    )
    assert resp.status_code == 200
    issue_id = resp.json()["id"]

    # A adds B as member (A is manager)
    resp = client.post(
        f"/api/projects/{project_id}/members",
        json={"email": "bob@example.com", "role": "developer"},
        headers=headers_a,
    )
    assert resp.status_code == 200

    # now B can see issues
    resp = client.get(f"/api/projects/{project_id}/issues", headers=headers_b)
    assert resp.status_code == 200
    issues = resp.json()
    assert any(i["id"] == issue_id for i in issues)

    # B tries to change status -> should be forbidden (not manager)
    resp = client.patch(
        f"/api/issues/{issue_id}",
        json={"status": "in_progress"},
        headers=headers_b,
    )
    assert resp.status_code == 403

    # A (manager) can change status
    resp = client.patch(
        f"/api/issues/{issue_id}",
        json={"status": "in_progress"},
        headers=headers_a,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"
