# Generated by Django 3.2.12 on 2022-04-07 02:32

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20220330_1955'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAlertMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('W', 'Warning (yellow)'), ('U', 'Urgent (red)'), ('N', 'Notice (blue)')], default='W', help_text='Defines the visual style of the message.', max_length=1)),
                ('content', tinymce.models.HTMLField(blank=True, help_text='Message that will be shown at the login page (max 400 characters).', max_length=400, null=True)),
                ('published', models.BooleanField(default=False, help_text='Sets if the message visible to all users.')),
                ('archived', models.BooleanField(default=False, help_text='Sets if the message is archived and should not be automatically evaluated.')),
                ('show_dates', models.BooleanField(default=True, help_text='Sets if the start and end dates should be visible in the alert message.')),
                ('start_date', models.DateTimeField(blank=True, help_text="Date and time of when the message should START being displayed. This will also automatically set 'published' status to True.", null=True, verbose_name='start date')),
                ('end_date', models.DateTimeField(blank=True, help_text="Date and time of when the message should STOP being displayed.  This will also automatically set the 'published' status to False.", null=True, verbose_name='end date')),
                ('custom_order', models.PositiveIntegerField(default=0, verbose_name='custom order')),
            ],
            options={
                'ordering': ['custom_order'],
            },
        ),
    ]