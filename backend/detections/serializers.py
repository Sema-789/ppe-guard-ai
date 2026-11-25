from rest_framework import serializers
from .models import ScanLog, Violation


class ScanLogSerializer(serializers.ModelSerializer):
    camera_code = serializers.CharField(source="camera.code", read_only=True)

    class Meta:
        model = ScanLog
        fields = [
            "id",
            "camera",
            "camera_code",
            "scanned_at",
            "total_persons",
            "compliant_persons",
            "is_compliant",
            "inference_ms",
            "snapshot",
        ]


class ViolationSerializer(serializers.ModelSerializer):
    camera_code = serializers.CharField(source="camera.code", read_only=True)
    reviewed_by_username = serializers.CharField(source="reviewed_by.username", read_only=True)

    class Meta:
        model = Violation
        fields = [
            "id",
            "scan_log",
            "camera",
            "camera_code",
            "violation_type",
            "confidence",
            "status",
            "bbox_json",
            "snapshot",
            "reviewed_by",
            "reviewed_by_username",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["reviewed_by", "reviewed_at", "created_at"]

class DetectionAnalyzeRequestSerializer(serializers.Serializer):
    camera = serializers.IntegerField()
    image = serializers.FileField()