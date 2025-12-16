# 🐞 IssueHub – Minimal Bug Tracker

![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169C1?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

A **minimal full-stack issue tracking system** built as an assignment to demonstrate **production-style backend architecture, authentication, and role-based access control**.

> Focus areas: API design, data modeling, RBAC, and maintainable project structure — not UI polish.

---

## ✨ Features

- 🔐 JWT-based authentication (OAuth2 password flow)
- 👥 Role-based access control (Viewer / Developer / Manager)
- 📁 Project management with member assignments
- 🐛 Issue tracking with status & priority
- 💬 Commenting system
- 📜 Auto-generated API docs (FastAPI Swagger UI)
- 🧪 Backend test coverage with Pytest

---

## 🧱 Tech Stack & Design Choices

### Backend
- **FastAPI** – async-first, typed, production-ready API framework
- **SQLAlchemy** – ORM with explicit models and relationships
- **PostgreSQL** (SQLite supported for local development)
- **JWT (OAuth2 Password Flow)** for stateless authentication

**Why FastAPI?**  
Strong typing, dependency injection, and automatic API documentation make it a good fit for maintainable production services.

**Trade-off:**  
More boilerplate (schemas, dependencies, CRUD layers) compared to Flask, accepted intentionally for clarity and scalability.

---

### Frontend
- **React + TypeScript**
- **Vite** for fast builds and minimal configuration
- **Axios** with a centralized HTTP client

**Design decision:**  
No Redux or Router. State is kept local and centralized in `App.tsx` to align with the “minimal bug tracker” scope.

---

### Authorization & RBAC
- Database enums:
  - `RoleEnum`: `viewer | developer | manager`
  - `IssueStatusEnum`: `open | in_progress | closed`
  - `PriorityEnum`: `low | medium | high`
- Only **Managers (Maintainers)** can update issue status or priority.

---

## 🎨 Styling

- Plain **CSS**
- Simple **two-column layout**
  - Left: projects & members
  - Right: issues & comments

**Trade-off:**  
No UI framework to keep dependencies minimal and code transparent.
---

### Main flows:

1. **Sign up / log in**.  
2. **Create a project** (name, key, description).  
3. **Create issues** under a project (title, description, priority).  
4. **Add comments** on an issue.  
5. **Add members** by email; set role to **MAINTAINER** (manager) for those who can change status/priority.  
6. **Update status** (`open`, `in_progress`, `closed`) as a manager.

---

## ✅ Tests

Backend tests live under `app/tests/` and use FastAPI’s `TestClient` with a separate test database.


---

## ⚙️ Setup Instructions

## 1️⃣ Backend Setup

### Requirements
- Python **3.10+**
- PostgreSQL *(SQLite supported for local runs)*

### Environment Variables
Create a `.env` file in the backend root:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/issuehub
SECRET_KEY=changeme-for-jwt
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### For SQLite:
```env 
DATABASE_URL=sqlite:///./issuehub.db
```

### Install Dependencies
```env 
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database Initialization
For this assignment, tables are created automatically on startup:
```env 
models.Base.metadata.create_all(bind=engine)
```
⚠️ In production, this should be replaced with Alembic migrations.

---

2️⃣ Frontend Setup

### Requirements

- Node 18+
- npm or yarn
```env 
cd frontend
npm install
npm run dev
```
Frontend runs on http://localhost:5173 ↗

Backend runs on http://localhost:8000 ↗

Axios injects the JWT token automatically:
```env 
const api = axios.create({
  baseURL: "http://localhost:8000",
});
```

---
▶️ Running the Application
### Backend
```env
uvicorn app.main:app --reload --port 8000
```
- API docs: http://localhost:8000/docs ↗

### Frontend
```env
npm run dev
```
---
### 🔌 API Docs (Swagger): `http://localhost:8000/docs`

### Main routes:

### Authentication
- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`

### Projects

- `GET /api/projects`
- `POST /api/projects`
- `POST /api/projects/{project_id}/members`
- `GET /api/projects/{project_id}/members`

### Issues

- `GET /api/projects/{project_id}/issues`
- `POST /api/projects/{project_id}/issues`
- `GET /api/issues/{issue_id}`
- `PATCH /api/issues/{issue_id}`
- `DELETE /api/issues/{issue_id}`

### Comments

- `GET /api/issues/{issue_id}/comments`
- `POST /api/issues/{issue_id}/comments`
---
### 🧪 Tests

Tests are located under `tests/`

Uses FastAPI `TestClient`

Covers authentication, projects, issues, comments, and RBAC rules

```env
pytest
```
---
### 🚧 Known Limitations & Possible Extensions

**Current Limitations:**

- `No Alembic migrations`
- `JWTs stored in localStorage`
- `No routing or pagination`
- `Comments are append-only`
- `No Docker or CI/CD`

**Possible Extensions:**

- `Alembic migrations`
- `Refresh tokens`
- `Issue filtering`
- `Docker + GitHub Actions`
- `Better RBAC`

