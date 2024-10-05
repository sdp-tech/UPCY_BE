# Generated by Django 5.1.1 on 2024-10-05 03:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("market", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdditionalImage",
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
                ("image", models.FileField(upload_to="additional_image")),
            ],
            options={
                "db_table": "additional_image",
            },
        ),
        migrations.CreateModel(
            name="DeliveryInformation",
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
                ("delivery_company", models.CharField(max_length=50, null=True)),
                (
                    "delivery_tracking_number",
                    models.CharField(max_length=50, null=True),
                ),
            ],
            options={
                "db_table": "delivery_information",
            },
        ),
        migrations.CreateModel(
            name="OptionCategory",
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
                ("option_category", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "option_category",
            },
        ),
        migrations.CreateModel(
            name="OrderImage",
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
                ("image", models.FileField(upload_to="order_image")),
            ],
            options={
                "db_table": "order_image",
            },
        ),
        migrations.CreateModel(
            name="OrderReformTexture",
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
                ("texture_name", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "order_reform_texture",
            },
        ),
        migrations.CreateModel(
            name="OrderState",
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
                    "reformer_status",
                    models.CharField(
                        choices=[
                            ("accepted", "수락"),
                            ("rejected", "거절"),
                            ("pending", "대기"),
                            ("received", "재료 수령"),
                            ("produced", "제작완료"),
                            ("deliver", "배송중"),
                            ("end", "거래 완료"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
            ],
            options={
                "db_table": "order_state",
            },
        ),
        migrations.CreateModel(
            name="TransactionOption",
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
                    "transaction_option",
                    models.CharField(
                        choices=[("pickup", "대면"), ("delivery", "택배")],
                        max_length=50,
                    ),
                ),
                ("delivery_address", models.TextField()),
                ("delivery_name", models.TextField()),
                ("delivery_phone_number", models.TextField()),
            ],
            options={
                "db_table": "transaction_option",
            },
        ),
        migrations.CreateModel(
            name="Order",
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
                ("additional_request", models.TextField(null=True)),
                ("total_price", models.IntegerField()),
                ("request_date", models.DateField()),
                ("kakaotalk_openchat_link", models.TextField(null=True)),
                (
                    "additional_option",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="additional_option_order",
                        to="market.serviceoption",
                    ),
                ),
            ],
            options={
                "db_table": "order",
            },
        ),
    ]
