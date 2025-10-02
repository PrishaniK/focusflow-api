# FocusFlow API

A timeline-agnostic study planner API built with **Django + Django REST Framework**.  
Learners can create **Subjects → Topics → Tasks**, run **timed Sessions**, and (next) get analytics like a weekly **Study Blueprint**.

- **Docs (Swagger):** `/api/docs/`
- **Auth:** JWT (`/auth/jwt/create/`, `/auth/jwt/refresh/`)

---

## Features (current MVP)
- JWT auth with per-user data isolation
- CRUD for **Subjects, Topics, Tasks**
- **Sessions**: start (`POST /sessions/`) and stop (`PATCH /sessions/{id}/stop/`) with minutes auto-computed
- Pagination (page number), standard error format, OpenAPI schema

**Coming next**
- `/me/summary` (window minutes, streak, due soon)
- `/me/blueprint` (deadline-optional “next up” ranking)
- Filters/search/ordering polish, basic tests, deployment

---

## Tech stack
- Python • Django • Django REST Framework
- djangorestframework-simplejwt (JWT auth)
- drf-spectacular (OpenAPI/Swagger)

---

## Project structure
focusflow-api/
├─ config/ # Django project (settings/urls)
├─ planner/ # App with models/serializers/views
│ ├─ models.py # Subject, Topic, Task, Session
│ ├─ serializers.py
│ ├─ views.py
│ └─ migrations/
├─ manage.py
└─ db.sqlite3 # local dev DB (ignored in production)

---

## Getting started (local)

> You can run this with or without a virtual environment.  

### 1) Install dependencies
```bash
# Windows
py -m pip install --user django djangorestframework djangorestframework-simplejwt drf-spectacular
# macOS/Linux
python3 -m pip install --user django djangorestframework djangorestframework-simplejwt drf-spectacular
2) Migrate & create a user
bash
Copy code
python manage.py migrate
python manage.py createsuperuser
3) Run
bash
Copy code
python manage.py runserver
Open http://127.0.0.1:8000/api/docs/

Auth (JWT)
POST /auth/jwt/create/

json
Copy code
{ "username": "YOUR_USERNAME", "password": "YOUR_PASSWORD" }
→ {"access": "...", "refresh": "..."}

POST /auth/jwt/refresh/

json
Copy code
{ "refresh": "..." }
→ {"access": "..."}

Use the access token in Swagger’s Authorize dialog as:

php-template
Copy code
Bearer <access token>
Quickstart (create minimal data)
Subject

http
Copy code
POST /subjects/
{ "name": "Mathematics", "color": "#1E90FF" }
Topic

http
Copy code
POST /topics/
{ "subject": 1, "title": "Eigenvalues", "status": "TODO", "struggle_level": 2 }
Task

http
Copy code
POST /tasks/
{ "topic": 1, "title": "Past paper Q1–Q3", "priority": 3, "status": "TODO" }
Session → Stop

http
Copy code
POST  /sessions/          { "task": 1 }
PATCH /sessions/1/stop/   // minutes will be computed
Complete a task (optional)

http
Copy code
PATCH /tasks/1/complete/
API conventions
Pagination: page number (default size 20)

Status codes: 201 create, 200 read/update, 204 delete, 400/401/403/404 errors

Error body: { "detail": "...", "code": "..." }

Enums: status = TODO | DOING | DONE, priority = 1..3, struggle_level = 0..3

Development notes
All querysets are scoped to the authenticated user (privacy).

Session.minutes is computed on stop (server-side, not client-supplied).

Deleting a Topic/Task keeps related Sessions (FK set to NULL) to preserve history.

Roadmap
GET /me/summary (rolling window minutes, streak, recent activity, due soon)

GET /me/blueprint (priority/struggle/recency/urgency heuristic; deadline-optional)

Filtering/search/ordering with django-filter

Basic tests (ownership, actions, schema)

Deployment (PythonAnywhere / Render)

Commit style
Use conventional prefixes:

feat:, fix:, docs:, test:, chore:
Example:
feat(api): add sessions stop action with minutes computation

