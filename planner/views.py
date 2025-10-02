import math
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Subject, Topic, Task, Session
from .serializers import SubjectSerializer, TopicSerializer, TaskSerializer, SessionSerializer

class OwnedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SubjectViewSet(OwnedViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class TopicViewSet(OwnedViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filterset_fields = ("subject", "status")
    search_fields = ("title",)

class TaskViewSet(OwnedViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = ("topic", "status", "priority")
    search_fields = ("title",)
    ordering_fields = ("due_date", "priority", "id")

    @action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = "DONE"
        task.save()
        return Response(self.get_serializer(task).data)

class SessionViewSet(OwnedViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filterset_fields = ("topic", "task")

    @action(detail=True, methods=["patch"])
    def stop(self, request, pk=None):
        s = self.get_object()
        if s.ended_at:
            return Response({"detail": "Session already stopped.", "code": "ALREADY_STOPPED"},
                            status=status.HTTP_400_BAD_REQUEST)
        s.ended_at = timezone.now()
        seconds = (s.ended_at - s.started_at).total_seconds()
        s.minutes = max(0, math.ceil(seconds / 60))
        s.save()
        return Response(self.get_serializer(s).data)

