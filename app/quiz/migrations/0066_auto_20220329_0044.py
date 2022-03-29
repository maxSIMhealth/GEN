# Generated by Django 3.2.12 on 2022-03-29 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0065_auto_20220328_1943'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='additional_content',
            field=models.TextField(blank=True, help_text='Optional: additional text that will be shown under the main text content. (max 1000 characters).', max_length=1000, null=True, verbose_name='additional content'),
        ),
        migrations.AddField(
            model_name='question',
            name='additional_content_en',
            field=models.TextField(blank=True, help_text='Optional: additional text that will be shown under the main text content. (max 1000 characters).', max_length=1000, null=True, verbose_name='additional content'),
        ),
        migrations.AddField(
            model_name='question',
            name='additional_content_fr',
            field=models.TextField(blank=True, help_text='Optional: additional text that will be shown under the main text content. (max 1000 characters).', max_length=1000, null=True, verbose_name='additional content'),
        ),
        migrations.AlterField(
            model_name='question',
            name='content',
            field=models.TextField(help_text='Main text content of the question (max 1000 characters).', max_length=1000, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='question',
            name='content_en',
            field=models.TextField(help_text='Main text content of the question (max 1000 characters).', max_length=1000, null=True, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='question',
            name='content_fr',
            field=models.TextField(help_text='Main text content of the question (max 1000 characters).', max_length=1000, null=True, verbose_name='content'),
        ),
    ]
