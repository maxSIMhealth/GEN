# Generated by Django 3.0.3 on 2020-06-10 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0010_auto_20200610_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionattempt',
            name='multiplechoice_answer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='quiz.MCAnswer'),
        ),
    ]
