"""
URL configuration for the FocusFlow API.

This module wires up:
- Django Admin
- JWT auth endpoints (create/refresh)
- DRF router for core resources (subjects, topics, tasks, sessions)
- Read-only analytics endpoints (/me/summary, /me/blueprint)
- OpenAPI schema + Swagger UI via drf-spectacular
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from planner.views import SubjectViewSet, TopicViewSet, TaskViewSet, SessionViewSet
from planner.views_me import me_summary, me_blueprint
from accounts.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["auth"], summary="Obtain JWT access & refresh tokens")
class TaggedTokenObtainPairView(TokenObtainPairView):
    pass

@extend_schema(tags=["auth"], summary="Refresh expired access token using refresh token")
class TaggedTokenRefreshView(TokenRefreshView):
    pass

# ---------------------------------------------------------------------------
# DRF ROUTER
# ---------------------------------------------------------------------------
# DefaultRouter generates RESTful routes like:
#   GET    /subjects/           → list
#   POST   /subjects/           → create
#   GET    /subjects/{id}/      → retrieve
#   PUT    /subjects/{id}/      → update
#   PATCH  /subjects/{id}/      → partial_update
#   DELETE /subjects/{id}/      → destroy
#
# The same pattern applies to topics, tasks, and sessions.
router = DefaultRouter()
router.register("subjects", SubjectViewSet)
router.register("topics", TopicViewSet)
router.register("tasks", TaskViewSet)
router.register("sessions", SessionViewSet)

# ---------------------------------------------------------------------------
# URL PATTERNS
# ---------------------------------------------------------------------------
urlpatterns = [
    # Django admin (useful for manual data inspection during review).
    path('admin/', admin.site.urls),
    # ---------- Auth (JWT) ----------
    path("auth/register/", RegisterView.as_view()),
    # Obtain a pair of tokens (access + refresh) by POSTing valid credentials.
    path('auth/jwt/create/', TaggedTokenObtainPairView.as_view()),
    # Refresh the short-lived access token using a valid refresh token.
    path('auth/jwt/refresh/', TaggedTokenRefreshView.as_view()),
    
    # ---------- API Schema & Docs ----------
    # Raw OpenAPI 3 schema (JSON). Useful for tooling/clients.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Interactive Swagger UI backed by the schema above.
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    
    # ---------- Core REST resources ----------
    # All CRUD endpoints from the DRF router (subjects/topics/tasks/sessions).
    path("", include(router.urls)),
    
    # ---------- Analytics (read-only) ----------
    # /me/summary/ returns rolling window minutes, streak, recent activity, etc.
    path("me/summary/", me_summary),
    # /me/blueprint/ returns “next up” tasks using the scoring heuristic.
    path("me/blueprint/", me_blueprint),
]
