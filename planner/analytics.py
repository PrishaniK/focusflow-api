from datetime import date, timedelta
from django.db.models import Sum
from .models import Task, Topic, Session

def window_minutes(user, window_days=7):
    """
    Aggregate total minutes and day-by-day activity for a rolling window.

    Args:
        user: Django User whose sessions we analyze.
        window_days: Number of days ending today to include (default 7).

    Returns:
        (total_minutes, recent_activity)
        - total_minutes (int): Sum of Session.minutes within the window.
        - recent_activity (list[dict]): One item per day in the window, in
          chronological order:
              [{"date": "YYYY-MM-DD", "minutes": <int>}, ...]

    Notes:
        * We filter only sessions that have ended (ended_at IS NOT NULL) so
          partial sessions don't skew totals.
        * We bin by started_at__date; that's sufficient for lightweight charts.
        * Using `date.today()` keeps this function timezone-agnostic.
    """
    since = date.today() - timedelta(days=window_days-1)
    
    # All finished sessions in the window.
    qs = Session.objects.filter(user=user, started_at__date__gte=since, ended_at__isnull=False)
    # Total minutes in the window (falls back to 0 if None).
    total = qs.aggregate(total=Sum("minutes"))["total"] or 0
    # Prepare daily buckets like ["2025-10-04", ..., "2025-10-10"].
    days = [(since + timedelta(d)).isoformat() for d in range(window_days)]
    minutes_by_day = {d: 0 for d in days}
    
    # One query to get minutes per day (grouped by started date).
    for s in qs.values("started_at__date").annotate(m=Sum("minutes")):
        minutes_by_day[s["started_at__date"].isoformat()] = s["m"] or 0
    recent_activity = [{"date": d, "minutes": minutes_by_day[d]} for d in days]
    return total, recent_activity

def study_streak(user):
    """
    Compute a simple "streak": consecutive days (ending today) where the user
    recorded any finished study session.

    Returns:
        int: Number of consecutive days of study. If today has no sessions but
        yesterday does, we allow the streak to continue through yesterday (one-day grace).

    Notes:
        * This is a lightweight heuristic, not a perfect "don't-break-the-chain".
        * If you want strict behavior, remove the one-day grace.
    """
    streak, delta = 0, 0
    while True:
        day = date.today() - timedelta(days=delta)
        has = Session.objects.filter(user=user, started_at__date=day, ended_at__isnull=False).exists()
        
        # Grace: if today is empty but yesterday had work, continue loop once.
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
        """
    Return the nearest upcoming tasks (optionally limited), ignoring completed ones.

    Args:
        user: Owner of tasks.
        limit: Maximum number of items to return.

    Returns:
        list[dict]: Light-weight task dicts with keys:
            id, title, due_date, priority, topic_id

    Ordering:
        * Earliest due_date first
        * For ties, higher priority first
    """
        return list(
            Task.objects.filter(user=user, status__in=["TODO", "DOING"])
            .exclude(due_date__isnull=True)
            .order_by("due_date", "-priority")[:limit]
            .values("id", "title", "due_date", "priority", "topic_id")
        )

def blueprint(user, limit=5):
    """
    Rank tasks by an explainable, deadline-optional score.

        score = 0.45*priority + 0.30*struggle + 0.15*recency + 0.10*urgency

    Where:
        * priority ∈ {1..3} (task-level; default 2 if missing)
        * struggle ∈ {0..3} (topic-level; default 0 if missing)
        * recency = 1 if the task's topic has NOT been studied in the last 7 days,
                    else 0 (i.e., we prefer topics you haven't touched recently)
        * urgency = 1 / max(1, days_to_due) if due_date exists, else 0

    Args:
        user: Owner of tasks.
        limit: Max number of tasks to return.

    Returns:
        list[dict]: Each item contains original task fields plus a float "score".
        Sorted descending by score, then tie-broken by:
            * earlier due date
            * higher priority
            * not recently studied
    """
    import math
    recent_since = date.today() - timedelta(days=7)

    # Precompute which topics have recent study (used to derive recency).
    topic_recent = set(
        Session.objects.filter(user=user, ended_at__isnull=False, started_at__date__gte=recent_since, topic__isnull=False)
        .values_list("topic_id", flat=True)
        .distinct()
    )
    
    # Pull only the fields we need; select_related helps if you expand later.
    rows = (
        Task.objects.select_related("topic", "topic__subject")
        .filter(user=user, status__in=["TODO", "DOING"])
        .values("id", "title", "priority", "due_date", "status", "topic_id")
    )

    out = []
    for r in rows:
        priority = r["priority"] or 2
        topic_id = r["topic_id"]
        
        # Topic.struggle_level is optional; default to 0 if missing or topic deleted.
        try:
            t = Topic.objects.get(id=topic_id, user=user)
            struggle = getattr(t, "struggle_level", 0) or 0
        except Topic.DoesNotExist:
            struggle = 0
            
        # If the topic was seen in the last 7 days, recency = 0; else 1.
        recency = 0 if topic_id in topic_recent else 1
        
        # Urgency rises as the due date approaches; 0 if no due date.
        if r["due_date"]:
            days_to_due = (r["due_date"] - date.today()).days
            urgency = 1.0 / max(1, days_to_due)
        else:
            urgency = 0.0
        score = 0.45*priority + 0.30*struggle + 0.15*recency + 0.10*urgency
        out.append({**r, "score": float(f"{score:.6f}")})

    # Sort by score desc, then earlier due date, then higher priority,
    # then prefer topics that were NOT recently studied.
    out.sort(key=lambda x: (-(x["score"]), x["due_date"] or date.max, -x["priority"], x["topic_id"] in topic_recent))
    return out[:limit]
