import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models


# Create your models here.
class UserAccountTypes(models.TextChoices):
    ADMIN = "admin"
    LEITOR = "leitor"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    complete_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=250, validators=[MinLengthValidator(8)])
    account_type = models.CharField(
        max_length=10, choices=UserAccountTypes.choices, default=UserAccountTypes.LEITOR
    )
    phone = models.CharField(max_length=16, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    first_name = None
    last_name = None
    last_login = None
    date_joined = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"
