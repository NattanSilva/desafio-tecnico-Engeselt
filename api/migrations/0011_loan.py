# Generated by Django 5.1.2 on 2024-11-03 17:26

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_book_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="Loan",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("expected_devolution_date", models.DateField()),
                ("devolution_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.BooleanField(
                        choices=[
                            ("pendente", "Pendente"),
                            ("em aberto", "Em Aberto"),
                            ("concluído", "Concluido"),
                        ],
                        default="pendente",
                    ),
                ),
                (
                    "observation",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="loans",
                        to="api.book",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="loans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
