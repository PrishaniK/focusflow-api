import math
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Subject, Topic, Task, Session
from .serializers import SubjectSerializer, TopicSerializer, TaskSerializer, SessionSerializer

class OwnedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that enforces per-user data isolation.

    - get_queryset(): scopes all list/retrieve/update/delete to request.user
    - perform_create(): stamps the new row with request.user

    Assumes each model inherits from OwnedModel with a `user` FK.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only ever operate on the authenticated user's rows.
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Never trust the client to set `user`; we set it server-side.
        serializer.save(user=self.request.user)

class SubjectViewSet(OwnedViewSet):
    """
    CRUD for Subjects (e.g., Mathematics, Biology).
    Unique per user by (user, name) at the model level.
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    
class TopicViewSet(OwnedViewSet):
    """
    CRUD for Topics (e.g., Eigenvalues under Mathematics).

    Filtering:
      - subject: filter by subject ID
      - status : TODO/DOING/DONE
    Search:
      - title (icontains) via DRF's SearchFilter if enabled globally.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filterset_fields = ("subject", "status")
    search_fields = ("title",)

class TaskViewSet(OwnedViewSet):
    """
    CRUD for Tasks (concrete study actions).

    Filtering:
      - topic, status, priority
    Search:
      - title (icontains)
    Ordering:
      - due_date, priority, id
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_fields = ("topic", "status", "priority")
    search_fields = ("title",)
    ordering_fields = ("due_date", "priority", "id")

    @action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        """
        PATCH /tasks/{id}/complete/

        Mark a task as DONE. Returns the updated serialized Task.
        """
        task = self.get_object()
        task.status = "DONE"
        task.save()
        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

class SessionViewSet(OwnedViewSet):
    """
    CRUD for Sessions (timed focus blocks).

    Notes:
      - Session.minutes is computed when you call the `stop` action.
      - Either `task` or `topic` may be provided (or both).
      - Related FKs are SET_NULL on delete to preserve history.
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filterset_fields = ("topic", "task")

    @action(detail=True, methods=["patch"])
    def stop(self, request, pk=None):
        """
        PATCH /sessions/{id}/stop/

        End a running session:
          - set ended_at = now
          - compute minutes = ceil((ended_at - started_at) / 60)
        Returns the updated serialized Session.

        Errors:
          - 400 if the session is already stopped.
        """
        s = self.get_object()

        if s.ended_at:
            return Response(
                {"detail": "Session already stopped.", "code": "ALREADY_STOPPED"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        s.ended_at = timezone.now()
        seconds = (s.ended_at - s.started_at).total_seconds()
        s.minutes = max(0, math.ceil(seconds / 60))
        s.save()

        return Response(self.get_serializer(s).data, status=status.HTTP_200_OK)

