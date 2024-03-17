# Generated by Django 4.0 on 2024-03-17 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icloud', '0011_alter_album_options_alter_album_name_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='imedia',
            constraint=models.UniqueConstraint(fields=('id', 'appleId'), name='unique_media_id_appleId'),
        ),
    ]