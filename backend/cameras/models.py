from django.db import models


class Camera(models.Model):
    class Status(models.TextChoices):
        ONLINE = "online", "Aktiv"
        OFFLINE = "offline", "Bağlantı yoxdur"
        ERROR = "error", "Xəta"

    code = models.CharField(max_length=30, unique=True)  # məs: CAM-01
    name = models.CharField(max_length=120)
    zone = models.CharField(max_length=120)              # məs: Sahə A / Qaynaq bölməsi
    stream_url = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ONLINE)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"