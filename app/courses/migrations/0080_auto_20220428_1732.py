# Generated by Django 3.2.13 on 2022-04-28 17:32

import tinymce.models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0079_remove_section_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="section",
            name="description",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Section description. Please try to keep it brief (under 1000 characters or 150 words).",
                null=True,
                verbose_name="description",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="description_en",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Section description. Please try to keep it brief (under 1000 characters or 150 words).",
                null=True,
                verbose_name="description",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="description_fr",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Section description. Please try to keep it brief (under 1000 characters or 150 words).",
                null=True,
                verbose_name="description",
            ),
        ),
    ]
