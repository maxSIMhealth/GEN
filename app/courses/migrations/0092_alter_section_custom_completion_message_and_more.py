# Generated by Django 4.0.10 on 2023-04-18 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0091_section_custom_completion_message_replace"),
    ]

    operations = [
        migrations.AlterField(
            model_name="section",
            name="custom_completion_message",
            field=models.CharField(
                blank=True,
                help_text="A custom message to be displayed after the participant has successfully completed the section. (max 200 characters)",
                max_length=200,
                verbose_name="Custom completion message",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="custom_completion_message_en",
            field=models.CharField(
                blank=True,
                help_text="A custom message to be displayed after the participant has successfully completed the section. (max 200 characters)",
                max_length=200,
                null=True,
                verbose_name="Custom completion message",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="custom_completion_message_fr",
            field=models.CharField(
                blank=True,
                help_text="A custom message to be displayed after the participant has successfully completed the section. (max 200 characters)",
                max_length=200,
                null=True,
                verbose_name="Custom completion message",
            ),
        ),
        migrations.AlterField(
            model_name="section",
            name="custom_completion_message_replace",
            field=models.BooleanField(
                default=False,
                help_text="Defines if the custom completion message should replace the default completion message or be displayed along side it.",
                verbose_name="Replace completion message with custom completion message",
            ),
        ),
    ]
