# Generated by Django 3.2.7 on 2021-12-01 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0066_course_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='paginate',
            field=models.BooleanField(default=True, help_text='* FOR CONTENT SECTION ONLY *: Define if section items should be paginated.', verbose_name='paginate items'),
        ),
    ]
