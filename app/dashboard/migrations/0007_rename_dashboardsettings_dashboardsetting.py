# Generated by Django 3.2.7 on 2021-12-05 17:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_dashboardsettings_active'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DashboardSettings',
            new_name='DashboardSetting',
        ),
    ]
