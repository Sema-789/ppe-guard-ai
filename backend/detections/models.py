from django.conf import settings
from django.db import models
from cameras.models import Camera


class ScanLog(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="scan_logs")
    scanned_at = models.DateTimeField(auto_now_add=True)
    total_persons = models.PositiveIntegerField(default=0)
    compliant_persons = models.PositiveIntegerField(default=0)
    is_compliant = models.BooleanField(default=True)
    inference_ms = models.FloatField(null=True, blank=True)
    snapshot = models.ImageField(upload_to="snapshots/%Y/%m/%d/", null=True, blank=True)

    def __str__(self):
        return f"Scan #{self.id} - {self.camera.code} ({self.scanned_at:%Y-%m-%d %H:%M})"


class Violation(models.Model):
    class ViolationType(models.TextChoices):
        NO_HELMET = "no_helmet", "Baret yoxdur"
        NO_VEST = "no_vest", "Təhlükəsizlik jileti yoxdur"
        MISSING_PPE = "missing_ppe", "Əskik PPE"

    class Status(models.TextChoices):
        OPEN = "open", "Açıq"
        ACKNOWLEDGED = "acknowledged", "Qəbul edildi"
        FALSE_POSITIVE = "false_positive", "Səhv pozitiv"
        RESOLVED = "resolved", "Həll olundu"

    scan_log = models.ForeignKey(
        ScanLog, on_delete=models.SET_NULL, null=True, blank=True, related_name="violations"
    )
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="violations")
    violation_type = models.CharField(max_length=30, choices=ViolationType.choices)
    confidence = models.FloatField()  # 0.0 - 1.0 və ya 0 - 100 aralığı
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    bbox_json = models.JSONField(null=True, blank=True)
    snapshot = models.ImageField(upload_to="violations/%Y/%m/%d/", null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_violations",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_violation_type_display()} ({self.confidence:.2f}) - {self.camera.code}"