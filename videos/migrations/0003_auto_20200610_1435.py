# Generated by Django 3.0.3 on 2020-06-10 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_videofile_original_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videofile',
            name='original_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='video file original name'),
        ),
    ]
