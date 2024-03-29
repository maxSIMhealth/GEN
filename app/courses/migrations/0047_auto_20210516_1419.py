# Generated by Django 3.1.8 on 2021-05-16 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0046_auto_20210515_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='pre_assessment',
            field=models.BooleanField(default=False, help_text='* FOR QUIZ SECTION ONLY *: Is this section a pre-assessment to evaluate if the learner needs to go through the course/module?', verbose_name='pre-assessment'),
        ),
        migrations.AlterField(
            model_name='section',
            name='create_discussions',
            field=models.BooleanField(default=False, help_text="* FOR UPLOAD SECTION ONLY *: automatically create a discussion board based on participant's video submissions. ", verbose_name='create discussion'),
        ),
    ]
