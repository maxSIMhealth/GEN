# Generated by Django 3.0.7 on 2020-09-03 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0033_quiz_require_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='allow_multiple_attempts',
            field=models.BooleanField(default=False, verbose_name='Allow multiple attempts'),
        ),
    ]