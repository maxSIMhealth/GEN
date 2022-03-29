# Generated by Django 3.2.7 on 2021-12-04 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_rename_dashboard_dashboardsettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardsettings',
            name='active',
            field=models.BooleanField(help_text='Set this setting as the active one. **WARNING**: only one setting can be set as active.', verbose_name='active'),
        ),
    ]