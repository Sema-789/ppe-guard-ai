from django.shortcuts import render

from django.db.models import Avg
from rest_framework.response import Response
from rest_framework.views import APIView

from cameras.models import Camera
from detections.models import ScanLog, Violation


class DashboardSummaryView(APIView):
    def get(self, request):
        total_cameras = Camera.objects.count()
        active_cameras = Camera.objects.filter(is_active=True, status=Camera.Status.ONLINE).count()
        total_scans = ScanLog.objects.count()
        compliant_scans = ScanLog.objects.filter(is_compliant=True).count()
        open_violations = Violation.objects.filter(status=Violation.Status.OPEN).count()
        total_violations = Violation.objects.count()
        avg_confidence = Violation.objects.aggregate(avg=Avg("confidence"))["avg"] or 0.0

        compliance_rate = round((compliant_scans / total_scans) * 100, 1) if total_scans > 0 else 100.0

        return Response({
            "cameras": {
                "total": total_cameras,
                "active": active_cameras,
            },
            "scans": {
                "total": total_scans,
                "compliant": compliant_scans,
                "compliance_rate": compliance_rate,
            },
            "violations": {
                "total": total_violations,
                "open": open_violations,
                "avg_confidence": round(float(avg_confidence), 3),
            },
        })