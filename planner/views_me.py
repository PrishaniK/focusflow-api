from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .analytics import window_minutes, study_streak, due_soon_tasks, blueprint
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["me"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_summary(request):
    """
    Read-only analytics for the authenticated user.

    Query params:
      - window_days (int, optional, default=7, clamp 1..30):
          How many days ending today to include in the rolling summary.

    Returns (200):
      {
        "window_days": <int>,
        "window_mins": <int>,                # total minutes in window
        "streak": <int>,                     # consecutive study days (grace-aware)
        "recent_activity": [                 # daily buckets for simple charts
          {"date": "YYYY-MM-DD", "minutes": <int>}, ...
        ],
        "due_soon": [                        # nearest upcoming tasks (if any)
          {"id": <int>, "title": "...", "due_date": "YYYY-MM-DD", "priority": <int>, "topic_id": <int>}, ...
        ]
      }

    Errors:
      - 400 BAD_WINDOW if `window_days` is invalid.
      - 401 if not authenticated (handled by permission class).
    """
    # Parse and clamp the window length to a safe range (1..30).
    try:
        window_days = int(request.query_params.get("window_days", 7))
        window_days = max(1, min(window_days, 30))
    except ValueError:
        return Response({"detail": "window_days must be an integer 1..30", "code": "BAD_WINDOW"}, status=status.HTTP_400_BAD_REQUEST)

    total, recent_activity = window_minutes(request.user, window_days=window_days)
    streak = study_streak(request.user)
    due = due_soon_tasks(request.user, limit=5)
    return Response({
        "window_days": window_days,
        "window_mins": total,
        "streak": streak,
        "recent_activity": recent_activity,
        "due_soon": due,
    })

@extend_schema(tags=["me"])
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_blueprint(request):
        """
    Rank upcoming tasks for the authenticated user using the deadline-optional
    heuristic (priority, struggle, recency, urgency).

    Query params:
      - limit (int, optional, default=5, clamp 1..20):
          Max number of tasks to return.

    Returns (200):
      [
        {
          "id": <int>, "title": "...", "priority": <int>, "due_date": "YYYY-MM-DD" | null,
          "status": "TODO|DOING|DONE", "topic_id": <int>, "score": <float>
        },
        ...
      ]

    Errors:
      - 400 BAD_LIMIT if `limit` is invalid.
      - 401 if not authenticated (handled by permission class).
    """
    # Parse and clamp the result size to a safe range (1..20).  
        try:
            limit = int(request.query_params.get("limit", 5))
            limit = max(1, min(limit, 20))
        except ValueError:
            return Response({"detail": "limit must be an integer 1..20", "code": "BAD_LIMIT"}, status=status.HTTP_400_BAD_REQUEST)
        items = blueprint(request.user, limit=limit)
        return Response(items)
