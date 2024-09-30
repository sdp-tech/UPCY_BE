# Generated by Django 5.1.1 on 2024-09-20 15:09

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0005_serviceoption_option_uuid_serviceimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicematerial",
            name="material_uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AddField(
            model_name="servicestyle",
            name="style_uuid",
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
