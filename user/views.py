from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from user.models import User
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.views.decorators.csrf import ensure_csrf_cookie


@api_view(["POST"])
def login(request) -> Response:
    """Authenticates a user and returns a token if credentials are valid."""

    username = request.data.get("username")
    password = request.data.get("password")
    print(username, password)

    user = authenticate(request, username=username, password=password)
    print(user)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "role" : user.role})
    else:
        return Response(
            {"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
def sign_up(request) -> Response:
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Set the password using the validated data before saving
        user.set_password(serializer.validated_data.get("password"))
        user.save()

        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request) -> Response:
    return Response({"message": f"User {request.user.email} is authenticated"})


@api_view(["POST"])  # Use DRF's api_view decorator for REST APIs
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
def change_password(request):
    user = request.user

    if request.method == "POST":
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"detail": "Incorrect old password."}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password:
            return Response({"detail": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password changed successfully."})
    else:
        return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)  # Handle non-POST requests
