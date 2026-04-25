from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    # In a full microservice, roles might be a separate field or choices.
    # For simplicity, we can rely on is_staff for admin vs employee logic.
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')

    def __str__(self):
        return f"{self.username} ({self.role})"
