from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from accounts.permissions import IsHSEOrAdmin
from .models import  Camera, ScanLog, Violation
from .serializers import DetectionAnalyzeRequestSerializer, ScanLogSerializer, ViolationSerializer
from .services import analyze_image_and_log


class ScanLogViewSet(viewsets.ModelViewSet):
    queryset = ScanLog.objects.select_related("camera").all().order_by("-scanned_at")
    serializer_class = ScanLogSerializer


class ViolationViewSet(viewsets.ModelViewSet):
    queryset = Violation.objects.select_related("camera", "reviewed_by").all().order_by("-created_at")
    serializer_class = ViolationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get("status")
        camera_id = self.request.query_params.get("camera")
        violation_type = self.request.query_params.get("violation_type")

        if status_param:
            qs = qs.filter(status=status_param)
        if camera_id:
            qs = qs.filter(camera_id=camera_id)
        if violation_type:
            qs = qs.filter(violation_type=violation_type)
        return qs

    @action(detail=True, methods=["patch", "post"], permission_classes=[IsHSEOrAdmin])
    def review(self, request, pk=None):
        violation = self.get_object()
        new_status = request.data.get("status")
        valid_statuses = [choice[0] for choice in Violation.Status.choices]
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Etibarsız status. Seçimlər: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        violation.status = new_status
        violation.reviewed_by = request.user
        violation.reviewed_at = timezone.now()
        violation.save()
        return Response(self.get_serializer(violation).data)

class DetectionAnalyzeViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = DetectionAnalyzeRequestSerializer

    @action(detail=False, methods=["post"], url_path="analyze")
    def analyze(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        camera = get_object_or_404(Camera, pk=serializer.validated_data["camera"])
        image_file = serializer.validated_data["image"]

        result = analyze_image_and_log(camera, image_file)

        return Response(
            {
                "model_used": result["model_used"],
                "scan": ScanLogSerializer(result["scan"]).data,
                "violations": ViolationSerializer(result["violations"], many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )

