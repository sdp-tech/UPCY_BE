# Generated by Django 4.0 on 2023-11-28 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_sdp_admin',
            new_name='is_staff',
        ),
    ]
