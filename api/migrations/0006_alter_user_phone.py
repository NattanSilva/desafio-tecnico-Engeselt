# Generated by Django 5.1.2 on 2024-11-01 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0005_alter_user_groups_alter_user_user_permissions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
