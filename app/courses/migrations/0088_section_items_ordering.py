# Generated by Django 4.0.9 on 2023-02-03 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0087_section_show_mark_as_complete_instruction"),
    ]

    operations = [
        migrations.AddField(
            model_name="section",
            name="items_ordering",
            field=models.CharField(
                choices=[("CRE", "Creation date"), ("CUS", "Custom order")],
                default="CUS",
                help_text="* FOR DISCUSSION SECTION ONLY *: Set the order for displaying section items.",
                max_length=3,
                verbose_name="items ordering",
            ),
        ),
    ]
