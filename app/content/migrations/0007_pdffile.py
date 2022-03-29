# Generated by Django 3.2.12 on 2022-03-29 19:30

import core.support_methods
from django.db import migrations, models
import django.db.models.deletion
import upload_validator


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_imagefile'),
    ]

    operations = [
        migrations.CreateModel(
            name='PdfFile',
            fields=[
                ('contentitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='content.contentitem')),
                ('file', models.FileField(help_text='Format accepted: PDF.', upload_to=core.support_methods.user_directory_path, validators=[upload_validator.FileTypeValidator(allowed_types=['application/pdf'])], verbose_name='pdf')),
            ],
            options={
                'abstract': False,
            },
            bases=('content.contentitem',),
        ),
    ]