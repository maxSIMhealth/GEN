# Generated by Django 3.0.7 on 2020-06-13 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0015_auto_20200613_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionattempt',
            name='multiplechoice_answers',
            field=models.ManyToManyField(blank=True, to='quiz.MCAnswer'),
        ),
    ]