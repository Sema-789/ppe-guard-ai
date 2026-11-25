from django.shortcuts import render
from rest_framework import viewsets
from .models import Camera
from .serializers import CameraSerializer
from rest_framework import permissions, viewsets
from accounts.permissions import IsAdminOnly, IsHSEOrAdmin
from .models import Camera
from .serializers import CameraSerializer


class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all().order_by("code")
    serializer_class = CameraSerializer

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all().order_by("code")
    serializer_class = CameraSerializer

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsAdminOnly]
        elif self.action in ("create", "update", "partial_update"):
            permission_classes = [IsHSEOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]