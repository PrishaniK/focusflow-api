from rest_framework import serializers
from .models import Subject, Topic, Task, Session

class OwnedSerializer(serializers.ModelSerializer):
    """
    Base serializer that automatically stamps the authenticated user on create.

    Why:
      - Every domain model inherits from OwnedModel (has a `user` FK).
      - We never trust clients to submit `user`; we set it from the request.

    Notes:
      - This assumes the serializer is used within a DRF View/Action
        with a request in `self.context["request"]`.
    """
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class SubjectSerializer(OwnedSerializer):
    """
    Serializer for Subject.

    - Exposes all fields (including `user`) but marks `user` as read-only,
      so clients can *see* ownership but cannot set/alter it.
    """
    class Meta:
        model = Subject
        fields = "__all__"
        read_only_fields = ("user",)

class TopicSerializer(OwnedSerializer):
    """
    Serializer for Topic.

    - `user` is read-only (set server-side).
    - Validates the usual model constraints via ModelSerializer.
    """
    class Meta:
        model = Topic
        fields = "__all__"
        read_only_fields = ("user",)

class TaskSerializer(OwnedSerializer):
    """
    Serializer for Task.

    - `user` is read-only (set server-side).
    - Model constraints handle uniqueness; you can optionally add extra
      serializer-level validation (e.g., priority range) for nicer errors.
    """
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("user",)

class SessionSerializer(OwnedSerializer):
    """
    Serializer for Session.

    Read-only fields:
      - `user`     : set automatically from request
      - `minutes`  : computed on stop server-side
      - `started_at`, `ended_at` : timestamps managed by the API

    Notes:
      - Clients may provide either `task` or `topic` (or both). Business rules
        are enforced in the view action that stops the session (computing minutes).
    """
    class Meta:
        model = Session
        fields = "__all__"
        read_only_fields = ("user", "minutes", "started_at", "ended_at")

