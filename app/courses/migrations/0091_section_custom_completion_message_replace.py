# Generated by Django 4.0.10 on 2023-04-18 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "courses",
            "0090_rename_completion_message_section_custom_completion_message_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="section",
            name="custom_completion_message_replace",
            field=models.BooleanField(
                default=False,
                help_text="Defines if the custom completion message should replace the default completion message or be displayed along side it.",
                verbose_name="Replace completion message with custom message",
            ),
        ),
    ]
