# Generated by Django 3.0.7 on 2020-09-03 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0036_auto_20200903_1707'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='check_score',
            field=models.BooleanField(default=True, verbose_name='show score'),
        ),
    ]