# Generated by Django 3.2.12 on 2022-03-28 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0064_auto_20220328_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='feedback',
            field=models.TextField(blank=True, help_text='Feedback to be shown after the question has been answered.', verbose_name='feedback'),
        ),
        migrations.AlterField(
            model_name='question',
            name='feedback_en',
            field=models.TextField(blank=True, help_text='Feedback to be shown after the question has been answered.', null=True, verbose_name='feedback'),
        ),
        migrations.AlterField(
            model_name='question',
            name='feedback_fr',
            field=models.TextField(blank=True, help_text='Feedback to be shown after the question has been answered.', null=True, verbose_name='feedback'),
        ),
    ]
