# Generated by Django 4.2.8 on 2023-12-15 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0078_quiz_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='show_submissions_count',
            field=models.BooleanField(default=False, help_text='Defines if the total number of submissions should be visible to ALL users (including learners). If false, only the quiz author, instructors, and admins will be able to see this information.', verbose_name='show submissions count'),
        ),
    ]
