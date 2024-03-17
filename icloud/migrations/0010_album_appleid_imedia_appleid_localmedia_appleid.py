# Generated by Django 4.0 on 2024-03-17 02:42

from django.db import migrations
import simplepro.components.fields.char_field


class Migration(migrations.Migration):

    dependencies = [
        ('icloud', '0009_alter_appleid_passwd'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='appleId',
            field=simplepro.components.fields.char_field.CharField(max_length=48, null=True, verbose_name='AppleID'),
        ),
        migrations.AddField(
            model_name='imedia',
            name='appleId',
            field=simplepro.components.fields.char_field.CharField(max_length=48, null=True, verbose_name='AppleID'),
        ),
        migrations.AddField(
            model_name='localmedia',
            name='appleId',
            field=simplepro.components.fields.char_field.CharField(max_length=48, null=True, verbose_name='AppleID'),
        ),
    ]