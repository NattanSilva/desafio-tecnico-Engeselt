# Generated by Django 5.1.2 on 2024-11-03 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_loan"),
    ]

    operations = [
        migrations.AddField(
            model_name="loan",
            name="aproved_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
