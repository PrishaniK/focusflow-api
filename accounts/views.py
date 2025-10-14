from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserOut
from drf_spectacular.utils import extend_schema

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]  # public

    @extend_schema(request=RegisterSerializer, responses={201: UserOut})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserOut(user).data, status=status.HTTP_201_CREATED)
