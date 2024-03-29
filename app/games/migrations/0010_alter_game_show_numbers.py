# Generated by Django 4.0.4 on 2022-05-18 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0009_game_show_numbers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="show_numbers",
            field=models.BooleanField(
                default=True,
                help_text="*ONLY FOR 'COMPLETE THE TEXT BOXES' GAME*: Defines if the answer items should be numbered.",
            ),
        ),
    ]
