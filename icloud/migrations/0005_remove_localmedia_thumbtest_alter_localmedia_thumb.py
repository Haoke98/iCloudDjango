# Generated by Django 4.0 on 2024-01-18 15:45

from django.db import migrations
import simplepro.components.fields


class Migration(migrations.Migration):

    dependencies = [
        ('icloud', '0004_alter_localmedia_thumbtest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='localmedia',
            name='thumbTest',
        ),
        migrations.AlterField(
            model_name='localmedia',
            name='thumb',
            field=simplepro.components.fields.ImageField(blank=True, max_length=255, null=True, verbose_name='缩略图'),
        ),
    ]