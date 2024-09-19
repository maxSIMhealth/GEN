# Generated by Django 4.2.9 on 2024-01-18 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0017_alter_videofile_subtitle_alter_videofile_subtitle_en_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='videofile',
            name='mute_audio',
            field=models.BooleanField(default=False, help_text="Sets volume to 'mute', but can be manually adjusted by the user."),
        ),
    ]