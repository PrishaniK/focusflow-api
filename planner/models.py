from django.conf import settings
from django.db import models

# ---------------------------------------------------------------------------
# Status enum used by Topic and Task. Kept as simple choices for readability.
# ---------------------------------------------------------------------------
STATUS = [("TODO", "TODO"), ("DOING", "DOING"), ("DONE", "DONE")]

class OwnedModel(models.Model):
    """
    Abstract base model that attaches each row to a specific user.

    Why:
      - Enforces per-user ownership across all domain tables.
      - Makes scoping querysets by request.user straightforward.

    on_delete = CASCADE:
      - If a user account is deleted, their data is deleted too.
        (This fits our single-tenant-per-user design.)
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True  # no DB table for this; mixed into child models


class Subject(OwnedModel):
    """
    A high-level area of study (e.g., "Mathematics", "Biology").

    Constraints:
      unique_together (user, name)
        - The same user cannot create two subjects with the same name.
        - Different users can have subjects with identical names.
    """
    name = models.CharField(max_length=80)
    # HEX color for UI tagging (e.g., "#1E90FF"). Not validated beyond length.
    color = models.CharField(max_length=7, default="#888888")

    class Meta:
        unique_together = [("user", "name")]


class Topic(OwnedModel):
    """
    A sub-area within a subject (e.g., "Eigenvalues" under "Linear Algebra").

    Relationships:
      subject → CASCADE:
        - Deleting a subject deletes its topics (and, via Task, their tasks).

    Fields:
      status: simple Kanban-style stage (TODO/DOING/DONE).
      struggle_level: optional 0..3 difficulty signal for the blueprint heuristic.

    Constraints:
      unique_together (user, subject, title)
        - Prevents duplicates within the same subject for a given user.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=120)
    status = models.CharField(max_length=5, choices=STATUS, default="TODO")
    struggle_level = models.IntegerField(default=0)  # recommended range: 0..3

    class Meta:
        unique_together = [("user", "subject", "title")]


class Task(OwnedModel):
    """
    A concrete, actionable item tied to a topic (e.g., "Past paper Q1–Q3").

    Relationships:
      topic → CASCADE:
        - Deleting a topic deletes its tasks.
        - Sessions reference tasks via FK with SET_NULL to preserve history.

    Fields:
      due_date: optional; the system works without deadlines.
      priority: 1..3 (higher = more important), used by the blueprint heuristic.
      status: TODO/DOING/DONE.
      notes: free text.

    Indexes:
      (user, status, due_date) index speeds common list filters.

    Constraints:
      unique_together (user, topic, title) prevents duplicate task titles
      within the same topic for one user.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=160)
    due_date = models.DateField(null=True, blank=True)
    priority = models.PositiveSmallIntegerField(default=2)  # expected 1..3
    status = models.CharField(max_length=5, choices=STATUS, default="TODO")
    notes = models.TextField(blank=True, default="")

    class Meta:
        unique_together = [("user", "topic", "title")]
        indexes = [models.Index(fields=["user", "status", "due_date"])]


class Session(OwnedModel):
    """
    A timed focus session. Either 'task' or 'topic' may be set (or both).

    Relationships:
      topic / task → SET_NULL:
        - We keep the session record even if the related topic/task is deleted.
        - This preserves historical analytics (minutes, streaks, charts).

    Fields:
      started_at: set automatically when the row is created.
      ended_at: set when the session is stopped.
      minutes: computed server-side when stopping a session.
      notes: free text e.g., “distraction-free”, “reviewed chapter 2”.
    """
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    minutes = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")