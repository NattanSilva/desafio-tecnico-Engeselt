# Generated by Django 5.1.2 on 2024-11-03 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0008_book"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]