# Generated by Django 3.0.3 on 2020-05-23 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_auto_20200523_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionitem',
            name='name',
            field=models.CharField(max_length=80),
        ),
    ]
