# Generated by Django 5.1.2 on 2024-11-03 00:58

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0007_address"),
    ]

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=200, unique=True)),
                ("author", models.CharField(max_length=200)),
                ("isbn", models.CharField(max_length=13, unique=True)),
                ("editor", models.CharField(max_length=200)),
                ("year_publication", models.IntegerField()),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("Fantasia", "Fantasia"),
                            ("Ficção Científica", "Ficção Científica"),
                            ("Mistério", "Mistério"),
                            ("Romance", "Romance"),
                            ("Suspense", "Suspense"),
                            ("Não Ficção", "Não Ficção"),
                            ("Biografia", "Biografia"),
                            ("Histórico", "Histórico"),
                            ("Fantasia Romântica", "Fantasia Romântica"),
                            ("Jovem Adulto", "Jovem Adulto"),
                            ("Sem Genero", "Sem Genero"),
                        ],
                        default="Sem Genero",
                        max_length=200,
                    ),
                ),
                ("total_quantity", models.IntegerField(default=1)),
                ("available_quantity", models.IntegerField(default=0)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
