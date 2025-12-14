from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MANAGER
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN