# Generated by Django 2.1.5 on 2019-01-25 20:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forums', '0013_auto_20190125_1520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forum',
            name='url',
        ),
    ]