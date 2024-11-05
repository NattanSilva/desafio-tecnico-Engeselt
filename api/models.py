import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models


# Create your models here.
class UserAccountTypes(models.TextChoices):
    ADMIN = "admin"
    LEITOR = "leitor"


class BookGender(models.TextChoices):
    FANTASIA = "Fantasia"
    FICÇÃO_CIENTÍFICA = "Ficção Científica"
    MISTÉRIO = "Mistério"
    ROMANCE = "Romance"
    SUSPENSE = "Suspense"
    NÃO_FICÇÃO = "Não Ficção"
    BIOGRAFIA = "Biografia"
    HISTÓRICO = "Histórico"
    FANTASIA_ROMÂNTICA = "Fantasia Romântica"
    JOVEM_ADULTO = "Jovem Adulto"
    SEM_GENERO = "Sem Genero"


class LoanStatus(models.TextChoices):
    PENDENTE = "pendente"
    EM_ABERTO = "em aberto"
    CONCLUIDO = "concluído"


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


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cep = models.CharField(max_length=10)
    state = models.CharField(max_length=2)
    city = models.CharField(max_length=180)
    district = models.CharField(max_length=180)
    street = models.CharField(max_length=180)
    number = models.CharField(max_length=10)
    complement = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="address")

    def __str__(self):
        return f"{self.id}"


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    editor = models.CharField(max_length=200)
    year_publication = models.IntegerField()
    gender = models.CharField(
        max_length=200, choices=BookGender.choices, default=BookGender.SEM_GENERO
    )
    total_quantity = models.IntegerField(default=1)
    available_quantity = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.available_quantity is None:
            self.available_quantity = self.total_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}"


class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="loans")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="loans")
    expected_devolution_date = models.DateField(null=False)
    aproved_date = models.DateField(null=True, blank=True)
    devolution_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        choices=LoanStatus.choices, default=LoanStatus.PENDENTE
    )
    observation = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"
