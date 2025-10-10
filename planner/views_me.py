from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .analytics import window_minutes, study_streak, due_soon_tasks, blueprint

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_summary(request):
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

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_blueprint(request):
    try:
        limit = int(request.query_params.get("limit", 5))
        limit = max(1, min(limit, 20))
    except ValueError:
        return Response({"detail": "limit must be an integer 1..20", "code": "BAD_LIMIT"}, status=status.HTTP_400_BAD_REQUEST)
    items = blueprint(request.user, limit=limit)
    return Response(items)
