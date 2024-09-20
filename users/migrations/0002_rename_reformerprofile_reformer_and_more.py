# Generated by Django 5.1.1 on 2024-09-20 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0002_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ReformerProfile",
            new_name="Reformer",
        ),
        migrations.AlterModelTable(
            name="reformerawards",
            table="reformer_awards",
        ),
        migrations.AlterModelTable(
            name="reformercareer",
            table="reformer_career",
        ),
        migrations.AlterModelTable(
            name="reformercertification",
            table="reformer_certification",
        ),
        migrations.AlterModelTable(
            name="reformerfreelancer",
            table="reformer_freelancer",
        ),
        migrations.AlterModelTable(
            name="reformermaterial",
            table="reformer_material",
        ),
        migrations.AlterModelTable(
            name="reformerstyle",
            table="reformer_style",
        ),
    ]
