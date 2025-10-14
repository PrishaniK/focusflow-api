# FocusFlow API  
*A timeline-agnostic study-planning API built with Django & Django REST Framework.*

Learners can create **Subjects → Topics → Tasks**, run timed **Sessions**, and view analytics such as a weekly **Study Summary** and a **Study Blueprint** that ranks upcoming tasks by priority, difficulty, recency, and urgency.

---

## Live Documentation

**Swagger UI:** `/api/docs/`  
**Auth endpoints:**
- `POST /auth/jwt/create/` - obtain access & refresh tokens  
- `POST /auth/jwt/refresh/` - renew access token  

---

## Features

- JWT authentication with per-user data isolation  
- CRUD for Subjects, Topics, Tasks  
- Session tracking - start/stop focus sessions, auto-calculate minutes  
- User analytics:
- `/me/summary` - study streak, weekly window minutes, due-soon tasks  
- `/me/blueprint` - “next up” task ranking heuristic  
- Pagination, filtering, and OpenAPI documentation (via drf-spectacular)  
- Unique constraints: no duplicate subject names per user  
- Consistent error schema & status codes  

---

## Architecture Overview

### ERD (conceptual)

User ───< Subject ───< Topic ───< Task ───< Session


Each record belongs to a user.  
Deleting higher-level objects (like Topics or Tasks) preserves related Sessions to retain study history.

---

## Tech Stack

| Layer | Tools / Libraries |
|-------|-------------------|
| Core | Python 3.13, Django 5 |
| API | Django REST Framework (DRF) |
| Auth | djangorestframework-simplejwt |
| Docs | drf-spectacular |
| Filters | django-filter |
| DB | SQLite (dev), PostgreSQL (recommended for prod) |

---

## Project Structure

```text
focusflow-api/
├─ config/              # Django project (settings, urls, wsgi)
├─ planner/             # Main app (models, serializers, views)
│  ├─ models.py         # Subject, Topic, Task, Session
│  ├─ serializers.py
│  ├─ views.py
│  ├─ views_me.py       # /me/summary & /me/blueprint endpoints
│  ├─ analytics.py      # Streaks, recency, heuristics
│  └─ migrations/
├─ manage.py
└─ db.sqlite3           # Local dev database (ignored in prod)

---

## Getting Started (Local Setup)

You can run this either globally or inside a virtual environment.

### 1️. Install dependencies

**Windows**
```bash
py -m pip install --user django djangorestframework djangorestframework-simplejwt drf-spectacular django-filter


macOS / Linux

python3 -m pip install --user django djangorestframework djangorestframework-simplejwt drf-spectacular django-filter

2️. Migrate & create an admin user
python manage.py migrate
python manage.py createsuperuser

3️. Run the API
python manage.py runserver


Visit → http://127.0.0.1:8000/api/docs/

Authentication (JWT)

You can register, log in, and authenticate directly through the API — no admin panel required.

### 1. Register a new account (public)

```http
POST /auth/register/

POST /auth/register/ – create a new account (public)

Then POST /auth/jwt/create/ - to obtain tokens

Request

{
  "username": "learner1",
  "email": "l1@example.com",
  "password": "supersecure123"
}


Response

{
  "id": 2,
  "username": "learner1",
  "email": "l1@example.com"
}

2️. Obtain tokens (login)
POST /auth/jwt/create/


Request

{
  "username": "learner1",
  "password": "supersecure123"
}


Response

{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

3. Refresh access token
POST /auth/jwt/refresh/


Request

{
  "refresh": "your-refresh-token-here"
}


Response

{
  "access": "new-access-token"
}

4️. Authorize in Swagger

Visit http://127.0.0.1:8000/api/docs/
 → click Authorize →
enter your token as:

Bearer your-access-token

You can now access all authenticated endpoints:

/subjects/

/topics/

/tasks/

/sessions/

/me/summary/

/me/blueprint/

Create token
POST /auth/jwt/create/
{
  "username": "YOUR_USERNAME",
  "password": "YOUR_PASSWORD"
}


Response:

{ "access": "...", "refresh": "..." }

Refresh token
POST /auth/jwt/refresh/
{ "refresh": "..." }


Use your access token in Swagger Authorize → Bearer <access>

Quickstart Example
1️. Create a Subject
POST /subjects/
{ "name": "Mathematics", "color": "#1E90FF" }

2. Create a Topic
POST /topics/
{ "subject": 1, "title": "Eigenvalues", "status": "TODO", "struggle_level": 2 }

3️. Create a Task
POST /tasks/
{ "topic": 1, "title": "Past paper Q1-Q3", "priority": 3, "status": "TODO" }

4️. Start & Stop a Session
POST /sessions/
{ "task": 1 }

PATCH /sessions/1/stop/


Minutes are automatically computed from start → stop.

5. Mark a Task as Complete
PATCH /tasks/1/complete/

Analytics Endpoints
Study Summary
GET /me/summary/


Returns:

{
  "window_days": 7,
  "window_mins": 120,
  "streak": 3,
  "recent_activity": [
    {"date": "2025-10-04", "minutes": 30},
    {"date": "2025-10-05", "minutes": 45}
  ],
  "due_soon": [
    {"title": "Essay draft", "due_date": "2025-10-15"}
  ]
}

Study Blueprint
GET /me/blueprint/


Heuristic:

score = 0.45·priority + 0.30·struggle + 0.15·recency + 0.10·urgency


Returns a list of tasks sorted by “next best to study”.

API Conventions
Concept	Description
Pagination	Page-number (default size: 20)
Status Codes	201 = created, 200 = success, 204 = deleted, 400/401/403/404 = error
Error Schema	{ "detail": "...", "code": "..." }
Enums	`status = TODO
Development Notes

All queries are scoped to the authenticated user (data privacy).

Session.minutes is computed server-side — clients cannot tamper with it.

Deleting Topics or Tasks does not cascade delete Sessions (to keep history).

Analytics are lightweight, computed on demand, and cache-ready.

Roadmap
Milestone	Status
Core CRUD & JWT auth	Complete
Sessions (start/stop)	Complete
Analytics /me/summary & /me/blueprint	Complete
Filtering & search polish	In progress
Unit tests for ownership/actions/schema	In progress
Deployment (Render / PythonAnywhere)	Planned
Commit Style

Follow Conventional Commits:

Prefix	Meaning
feat:	new feature
fix:	bug fix
docs:	documentation change
test:	test added/updated
chore:	maintenance or config

Example:

feat(api): add session stop action with auto minutes calculation

Originality & Purpose

FocusFlow was built from scratch for the ALX Back-End Capstone.
It demonstrates data modeling, authentication, analytics, and clean RESTful design - all within a purely backend context.

No frontend is required for this capstone; the API is fully testable via Swagger or Postman, and designed to be easily integrated with a future frontend or mobile app.

License & Credits

© 2025 - ALX Back-End Capstone Project
Developed by Prishani
Libraries: Django, Django REST Framework, drf-spectacular, simplejwt, django-filter.