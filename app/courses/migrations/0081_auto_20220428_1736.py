# Generated by Django 3.2.13 on 2022-04-28 17:36

import tinymce.models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0080_auto_20220428_1732"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="description",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Course description. Please try to keep it brief (under 2000 characters).",
                null=True,
                verbose_name="description",
            ),
        ),
        migrations.AlterField(
            model_name="course",
            name="description_en",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Course description. Please try to keep it brief (under 2000 characters).",
                null=True,
                verbose_name="description",
            ),
        ),
        migrations.AlterField(
            model_name="course",
            name="description_fr",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Course description. Please try to keep it brief (under 2000 characters).",
                null=True,
                verbose_name="description",
            ),
        ),
    ]
