# Generated by Django 3.2.7 on 2021-12-04 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0068_auto_20211203_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='certificate_type',
            field=models.CharField(choices=[('CC', 'Certificate - Course'), ('CX', 'Certificate - Custom')], default='CC', help_text='Defines if the certificate provided will be for the current course or use a customized term.', max_length=2, verbose_name='certificate type'),
        ),
    ]