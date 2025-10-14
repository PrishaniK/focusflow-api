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
```
---

## Getting Started (Local Setup)

You can run this either globally or inside a virtual environment.

### 1️. Install dependencies

**Windows**
py -m pip install --user django djangorestframework djangorestframework-simplejwt drf-spectacular django-filter


**macOS / Linux**
python3 -m pip install --user django djangorestframework djangorestframework-simplejwt drf-spectacular django-filter

### 2️. Migrate & create an admin user
python manage.py migrate
python manage.py createsuperuser

### 3️. Run the API
python manage.py runserver


Open: http://127.0.0.1:8000/api/docs/

## Authentication (JWT)
You can register, log in, and authenticate directly through the API - no admin panel required.

### 1. Register a new account (public)
```
POST /auth/register/

Request:

{
  "username": "learner1",
  "email": "l1@example.com",
  "password": "supersecure123"
}

Response:

201 Created
{ "id": 2, "username": "learner1", "email": "l1@example.com" }

### 2. Obtain tokens (login)
POST /auth/jwt/create/
Request:
{ 
  "username": "learner1", 
  "password": "supersecure123" 
}

Response:
200 OK
{ "access": "…", "refresh": "…" }


### 3. Refresh access token

POST /auth/jwt/refresh/

Request:
{
  "refresh": "your-refresh-token-here"
}

Response

200 OK

{
  "access": "new-access-token"
}

### 4️. Authorize in Swagger

Visit http://127.0.0.1:8000/api/docs/
 → click Authorize →
enter your token as:

Bearer <your-access-token>

You can now access all authenticated endpoints:

/subjects/
/topics/
/tasks/
/sessions/
/me/summary/
/me/blueprint/


Quickstart Example

1️. Create a Subject

POST /subjects/

Request:

{ 
  "name": "Mathematics", 
  "color": "#1E90FF" 
}

Response:

201 Created

{ "id": 1, "name": "Mathematics", "color": "#1E90FF", "user": 2 }

2. Create a Topic

POST /topics/

Request:

{ 
  "title": "Eigenvalues & Eigenvectors",
  "status": "TODO", 
  "struggle_level": 2 
  "subject": 1 
}
Response:

201 Created
{ "id": 1, "subject": 1, "title": "Eigenvalues & Eigenvectors", "status": "TODO", "struggle_level": 2, "user": 2 }

3️. Create a Task (inside a topic)
- priority: 1..3 (3 = most important)
- status: "TODO" | "DOING" | "DONE"
- due_date: optional ISO date YYYY-MM-DD

POST /tasks/

Request:
{ 
  "title": "Past paper Q1–Q3", 
  "due_date": "2025-10-20", 
  "priority": 3, 
  "status": "TODO", 
  "notes": "", 
  "topic": 1 
}

Response:
201 Created
{
  "id": 1, "topic": 1, "title": "Past paper Q1–Q3",
  "priority": 3, "status": "TODO", "due_date": "2025-10-20",
  "notes": "", "user": 2
}

4️. Sessions (track focused study time)
POST /sessions/

Request:
{ 
  "notes": "Pomodoro #1", 
  "topic": 1, 
  "task": 1 
}

Response:
201 Created
{
  "id": 1, "task": 1, "topic": 1,
  "started_at": "2025-10-14T12:00:00Z",
  "ended_at": null, "minutes": 0, "notes": "Pomodoro #1", "user": 2
}

Stop the session - minutes are computed server-side.
PATCH /sessions/1/stop/

Minutes are automatically computed from start → stop.
Response:
200 OK
{
  "id": 1, "task": 1, "topic": 1,
  "started_at": "2025-10-14T12:00:00Z",
  "ended_at": "2025-10-14T12:42:12Z",
  "minutes": 43, "notes": "Pomodoro #1", "user": 2
}

5. Analytics (“Me”)
GET /me/summary/?window_days=7

Response:
{
  "window_days": 7,
  "window_mins": 120,
  "streak": 3,
  "recent_activity": [
    { "date": "2025-10-08", "minutes": 0 },
    { "date": "2025-10-09", "minutes": 45 },
    { "date": "2025-10-10", "minutes": 0 },
    { "date": "2025-10-11", "minutes": 30 },
    { "date": "2025-10-12", "minutes": 0 },
    { "date": "2025-10-13", "minutes": 45 },
    { "date": "2025-10-14", "minutes": 0 }
  ],
  "due_soon": [
    { "id": 1, "title": "Past paper Q1–Q3", "due_date": "2025-10-20", "priority": 3, "topic_id": 1 }
  ]
}

GET /me/blueprint/?limit=5

Ranks next tasks using a deadline-optional score:
0.45*priority + 0.30*struggle + 0.15*recency + 0.10*urgency

Tie-breakers: earlier due → higher priority → least recently studied.

Response:
200 OK
[
  {
    "id": 1,
    "title": "Past paper Q1–Q3",
    "priority": 3,
    "status": "TODO",
    "due_date": "2025-10-20",
    "topic_id": 1,
    "score": 2.550000
  }
]

```

#### Field ranges & enums (so Swagger’s placeholders don’t confuse you)
- status: "TODO" | "DOING" | "DONE"
- priority: integer 1..3 (default 2)
- struggle_level: integer 0..3 (default 0)
- due_date: optional; if absent, analytics still work (timeline-agnostic)


API Conventions
Concept	Description
Pagination	Page-number (default size: 20)
Status Codes	201 = created, 200 = success, 204 = deleted, 400/401/403/404 = error
Error Schema	{ "detail": "...", "code": "..." }
Enums	`status = TODO
Development Notes

All queries are scoped to the authenticated user (data privacy).
Session.minutes is computed server-side - clients cannot tamper with it.

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