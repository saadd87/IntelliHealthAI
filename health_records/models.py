from django.db import models
from django.contrib.auth.models import User


class HealthRecord(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    age = models.IntegerField()

    weight = models.FloatField()

    height = models.FloatField()

    blood_pressure = models.CharField(
        max_length=20
    )

    glucose_level = models.FloatField()

    risk = models.CharField(
    max_length=20,
    default='Unknown'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.username