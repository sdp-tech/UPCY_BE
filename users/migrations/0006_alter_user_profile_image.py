# Generated by Django 4.0 on 2024-01-10 11:44

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_user_area_alter_user_code_alter_user_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(default='user_profile_image.png', null=True, upload_to=users.models.get_upload_path),
        ),
    ]
