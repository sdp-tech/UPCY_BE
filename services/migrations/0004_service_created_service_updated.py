# Generated by Django 4.2.11 on 2024-03-20 11:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_service_max_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='service',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
