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

    @property
    def is_admin(self):
        """Property do szablonów i logiki biznesowej"""
        return self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        """
        Ustawia is_staff automatycznie:
        - każdy superuser zawsze ma is_staff=True
        - użytkownik z rolą ADMIN ma is_staff=True
        - reszta (np. Manager) ma is_staff=False
        """
        if self.is_superuser or self.role == self.Role.ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)