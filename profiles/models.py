from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        blank=True
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.user.username
