from django.conf import settings
from django.db import models

STATUS = [("TODO", "TODO"), ("DOING", "DOING"), ("DONE", "DONE")]

class OwnedModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class Meta:
        abstract = True

class Subject(OwnedModel):
    name = models.CharField(max_length=80)
    color = models.CharField(max_length=7, default="#888888")
    class Meta:
        unique_together = [("user", "name")]

class Topic(OwnedModel):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=120)
    status = models.CharField(max_length=5, choices=STATUS, default="TODO")
    struggle_level = models.IntegerField(default=0)  # 0..3
    class Meta:
        unique_together = [("user", "subject", "title")]

class Task(OwnedModel):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=160)
    due_date = models.DateField(null=True, blank=True)
    priority = models.PositiveSmallIntegerField(default=2)  # 1..3
    status = models.CharField(max_length=5, choices=STATUS, default="TODO")
    notes = models.TextField(blank=True, default="")
    class Meta:
        unique_together = [("user", "topic", "title")]
        indexes = [models.Index(fields=["user", "status", "due_date"])]

class Session(OwnedModel):
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    minutes = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, default="")

