from rest_framework import serializers
from .models import Subject, Topic, Task, Session

class OwnedSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class SubjectSerializer(OwnedSerializer):
    class Meta:
        model = Subject
        fields = "__all__"
        read_only_fields = ("user",)

class TopicSerializer(OwnedSerializer):
    class Meta:
        model = Topic
        fields = "__all__"
        read_only_fields = ("user",)

class TaskSerializer(OwnedSerializer):
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("user",)

class SessionSerializer(OwnedSerializer):
    class Meta:
        model = Session
        fields = "__all__"
        read_only_fields = ("user", "minutes", "started_at", "ended_at")

