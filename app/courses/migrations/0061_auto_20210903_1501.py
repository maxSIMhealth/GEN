# Generated by Django 3.1.13 on 2021-09-03 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0060_auto_20210730_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='description',
            field=models.TextField(help_text='Description (max 2000 characters)', max_length=2000, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='course',
            name='description_en',
            field=models.TextField(help_text='Description (max 2000 characters)', max_length=2000, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='course',
            name='description_fr',
            field=models.TextField(help_text='Description (max 2000 characters)', max_length=2000, null=True, verbose_name='description'),
        ),
    ]