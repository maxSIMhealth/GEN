# Generated by Django 3.0.3 on 2020-04-06 19:53

from django.db import migrations, models
import forums.models


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0025_auto_20200406_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='videofile',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=forums.models.user_directory_path),
        ),
    ]