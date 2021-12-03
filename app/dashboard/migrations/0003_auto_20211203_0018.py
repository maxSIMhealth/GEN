# Generated by Django 3.2.7 on 2021-12-03 00:18

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20211202_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='description',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dashboard',
            name='instructions',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
    ]
