# Generated by Django 3.1.13 on 2021-07-24 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0055_quiz_paginate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='openended_type',
            field=models.CharField(choices=[('OD', 'Open ended - Date'), ('ON', 'Open ended - Numeric'), ('OH', 'Opend ended - Time/hour'), ('OT', 'Open ended - Text (short)'), ('OA', 'Open ended - Text (long)')], default='OA', help_text='Type of open ended question.', max_length=2, verbose_name='Open ended type'),
        ),
    ]
