from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import DetectionAnalyzeViewSet, ScanLogViewSet, ViolationViewSet

router = DefaultRouter()
router.register("scans", ScanLogViewSet, basename="scan")
router.register("violations", ViolationViewSet, basename="violation")
router.register("", DetectionAnalyzeViewSet, basename="detection")

urlpatterns = [
    path("", include(router.urls)),
]