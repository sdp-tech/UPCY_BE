# Generated by Django 5.1.1 on 2024-09-18 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0007_alter_market_reformer"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="marketservice",
            name="reformer",
        ),
    ]
