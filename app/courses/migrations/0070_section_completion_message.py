# Generated by Django 3.2.7 on 2021-12-05 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0069_alter_course_certificate_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='completion_message',
            field=models.CharField(blank=True, help_text='A message to be displayed after the participant has successfully completed the section. (max 200 characters ', max_length=200, verbose_name='completion message'),
        ),
    ]
