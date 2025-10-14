from datetime import date, timedelta
from django.db.models import Sum
from .models import Task, Topic, Session

def window_minutes(user, window_days=7):
    since = date.today() - timedelta(days=window_days-1)
    qs = Session.objects.filter(user=user, started_at__date__gte=since, ended_at__isnull=False)
    total = qs.aggregate(total=Sum("minutes"))["total"] or 0
    # daily buckets (for simple charts later)
    days = [(since + timedelta(d)).isoformat() for d in range(window_days)]
    minutes_by_day = {d: 0 for d in days}
    for s in qs.values("started_at__date").annotate(m=Sum("minutes")):
        minutes_by_day[s["started_at__date"].isoformat()] = s["m"] or 0
    recent_activity = [{"date": d, "minutes": minutes_by_day[d]} for d in days]
    return total, recent_activity

def study_streak(user):
    # Count consecutive days (ending today) with any minutes
    streak, delta = 0, 0
    while True:
        day = date.today() - timedelta(days=delta)
        has = Session.objects.filter(user=user, started_at__date=day, ended_at__isnull=False).exists()
        if not has:
            # allow skip if today has no session yet (streak through yesterday)
            if delta == 0 and Session.objects.filter(user=user, started_at__date=date.today()-timedelta(days=1), ended_at__isnull=False).exists():
                delta += 1
                continue
            break
        streak += 1
        delta += 1
    return streak

def due_soon_tasks(user, limit=5):
    return list(
        Task.objects.filter(user=user, status__in=["TODO", "DOING"])
        .exclude(due_date__isnull=True)
        .order_by("due_date", "-priority")[:limit]
        .values("id", "title", "due_date", "priority", "topic_id")
    )

def blueprint(user, limit=5):
    """
    Deadline-optional score:
      score = 0.45*priority + 0.30*struggle + 0.15*recency + 0.10*urgency
    recency: 1 if task’s topic has not been studied in the last 7 days, else 0
    urgency: if due_date given => 1 / max(1, days_to_due), else 0
    """
    import math
    recent_since = date.today() - timedelta(days=7)

    # precompute topic recent-study
    topic_recent = set(
        Session.objects.filter(user=user, ended_at__isnull=False, started_at__date__gte=recent_since, topic__isnull=False)
        .values_list("topic_id", flat=True)
        .distinct()
    )
    rows = (
        Task.objects.select_related("topic", "topic__subject")
        .filter(user=user, status__in=["TODO", "DOING"])
        .values("id", "title", "priority", "due_date", "status", "topic_id")
    )

    out = []
    for r in rows:
        priority = r["priority"] or 2
        topic_id = r["topic_id"]
        # struggle from Topic (default 0)
        try:
            t = Topic.objects.get(id=topic_id, user=user)
            struggle = getattr(t, "struggle_level", 0) or 0
        except Topic.DoesNotExist:
            struggle = 0
        recency = 0 if topic_id in topic_recent else 1
        if r["due_date"]:
            days_to_due = (r["due_date"] - date.today()).days
            urgency = 1.0 / max(1, days_to_due)
        else:
            urgency = 0.0
        score = 0.45*priority + 0.30*struggle + 0.15*recency + 0.10*urgency
        out.append({**r, "score": float(f"{score:.6f}")})

    # tie-breakers: earlier due, higher priority, least recently studied
    out.sort(key=lambda x: (-(x["score"]), x["due_date"] or date.max, -x["priority"], x["topic_id"] in topic_recent))
    return out[:limit]
