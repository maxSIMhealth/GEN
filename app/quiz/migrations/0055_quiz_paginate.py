# Generated by Django 3.1.13 on 2021-07-24 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0054_question_openended_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='paginate',
            field=models.BooleanField(default=True, verbose_name='paginate questions'),
        ),
    ]
