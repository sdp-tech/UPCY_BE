# Generated by Django 5.1.4 on 2025-01-13 13:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("market", "0002_initial"),
        ("order", "0001_initial"),
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="order_reformer",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reformer_order",
                to="users.reformer",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="request_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="request_user_order",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="service_order",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="service_orders",
                to="market.service",
            ),
        ),
        migrations.AddField(
            model_name="deliveryinformation",
            name="service_order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="delivery_information",
                to="order.order",
            ),
        ),
        migrations.AddField(
            model_name="additionalimage",
            name="service_order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="additional_image",
                to="order.order",
            ),
        ),
        migrations.AddField(
            model_name="orderimage",
            name="service_order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_image",
                to="order.order",
            ),
        ),
        migrations.AddField(
            model_name="orderstate",
            name="service_order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_state",
                to="order.order",
            ),
        ),
        migrations.AddField(
            model_name="transactionoption",
            name="service_order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="transaction_option",
                to="order.order",
            ),
        ),
    ]
