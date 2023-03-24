# Generated by Django 4.0.8 on 2022-12-17 19:54

import tinymce.models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0073_alter_question_additional_content_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="feedback",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Feedback to be shown after the question has been answered.",
                verbose_name="feedback",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="feedback_en",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Feedback to be shown after the question has been answered.",
                null=True,
                verbose_name="feedback",
            ),
        ),
        migrations.AlterField(
            model_name="question",
            name="feedback_fr",
            field=tinymce.models.HTMLField(
                blank=True,
                help_text="Feedback to be shown after the question has been answered.",
                null=True,
                verbose_name="feedback",
            ),
        ),
    ]