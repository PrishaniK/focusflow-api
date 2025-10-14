from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    # write_only so password is never returned
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        # keep it simple: username + optional email + password
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        # creates user AND hashes password correctly
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

# (tiny output serializer so /auth/register/ shows a clean response body in Swagger)
class UserOut(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")
