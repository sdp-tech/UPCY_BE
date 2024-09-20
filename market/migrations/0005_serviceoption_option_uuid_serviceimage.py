# Generated by Django 5.1.1 on 2024-09-20 15:06

import django.db.models.deletion
import market.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0004_alter_market_reformer"),
    ]

    operations = [
        migrations.AddField(
            model_name="serviceoption",
            name="option_uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.CreateModel(
            name="ServiceImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    models.FileField(
                        upload_to=market.models.get_service_image_upload_path
                    ),
                ),
                (
                    "market_service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_image",
                        to="market.marketservice",
                    ),
                ),
            ],
            options={
                "db_table": "market_service_image",
            },
        ),
    ]
