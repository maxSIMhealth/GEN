# Generated by Django 3.0.3 on 2020-05-13 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0026_videofile_thumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videofile',
            name='author',
        ),
        migrations.RemoveField(
            model_name='videofile',
            name='course',
        ),
    ]
