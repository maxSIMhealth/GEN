# Generated by Django 3.1.3 on 2020-11-20 16:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0034_auto_20201120_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='learners',
            field=models.ManyToManyField(blank=True, related_name='learners', to=settings.AUTH_USER_MODEL, verbose_name='learners'),
        ),
    ]
