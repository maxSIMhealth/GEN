# Generated by Django 3.1.8 on 2021-05-16 15:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0047_auto_20210516_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='section',
            name='show_thumbnails',
            field=models.BooleanField(default=False, help_text='* FOR VIDEO AND UPLOAD SECTIONS ONLY *: enables displaying video thumbnails.', verbose_name='show thumbnails'),
        ),
        migrations.AlterField(
            model_name='status',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='status', to='courses.section', verbose_name='section'),
        ),
    ]
