from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserProfileSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "refresh token tələb olunur."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Etibarsız refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Çıxış uğurla tamamlandı."}, status=status.HTTP_200_OK)