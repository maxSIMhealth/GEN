# Generated by Django 4.0.4 on 2022-05-05 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0005_alter_movetocolumnsitem_text_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="movetocolumnsgroup",
            name="source_shuffle",
            field=models.BooleanField(
                default=False,
                help_text="Defines if the source items should be shuffled.",
            ),
        ),
    ]
