# Generated by Django 3.0.3 on 2020-04-28 17:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
        ('quiz', '0028_auto_20200427_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='likertattempt',
            name='course',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.PROTECT, to='courses.Course'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='likertattempt',
            name='quiz',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, to='quiz.Quiz'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='openendedattempt',
            name='course',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.PROTECT, to='courses.Course'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='openendedattempt',
            name='quiz',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, to='quiz.Quiz'),
            preserve_default=False,
        ),
    ]