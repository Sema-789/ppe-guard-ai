from django.db import models


class DailyComplianceSummary(models.Model):
    date = models.DateField(unique=True)
    total_scans = models.PositiveIntegerField(default=0)
    total_violations = models.PositiveIntegerField(default=0)
    false_positives = models.PositiveIntegerField(default=0)
    compliance_rate = models.FloatField(default=100.0)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - Uyğunluq: {self.compliance_rate:.1f}%"