# Generated by Django 3.0.3 on 2020-04-28 18:18

from django.db import migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0031_auto_20200428_1415'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mcanswer',
            options={'verbose_name': 'Multiple Choice Answer (scale)', 'verbose_name_plural': 'Multiple Choice Answers (scales)'},
        ),
        migrations.AddField(
            model_name='mcanswer',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='mcanswer',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
    ]
