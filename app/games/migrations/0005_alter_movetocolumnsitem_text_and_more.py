# Generated by Django 4.0.4 on 2022-05-05 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0004_auto_20220415_1556"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movetocolumnsitem",
            name="text",
            field=models.CharField(
                help_text="Item text description (max 250 characters)",
                max_length=250,
                verbose_name="text",
            ),
        ),
        migrations.AlterField(
            model_name="movetocolumnsitem",
            name="text_en",
            field=models.CharField(
                help_text="Item text description (max 250 characters)",
                max_length=250,
                null=True,
                verbose_name="text",
            ),
        ),
        migrations.AlterField(
            model_name="movetocolumnsitem",
            name="text_fr",
            field=models.CharField(
                help_text="Item text description (max 250 characters)",
                max_length=250,
                null=True,
                verbose_name="text",
            ),
        ),
        migrations.AlterField(
            model_name="textboxesterm",
            name="text",
            field=models.CharField(
                help_text="Item text description (max 250 characters)",
                max_length=250,
                verbose_name="text",
            ),
        ),
        migrations.AlterField(
            model_name="textboxesterm",
            name="text_en",
            field=models.CharField(
                help_text="Item text description (max 250 characters)",
                max_length=250,
                null=True,
                verbose_name="text",
            ),
        ),
        migrations.AlterField(
            model_name="textboxesterm",
            name="text_fr",
            field=models.CharField(
                help_text="Item text description (max 250 characters)",
                max_length=250,
                null=True,
                verbose_name="text",
            ),
        ),
    ]
