# Generated by Django 3.1.13 on 2021-09-18 18:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_imagefile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0058_auto_20210807_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='auth.user', verbose_name='author'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ForeignKey(blank=True, help_text='Optional image file.', null=True, on_delete=django.db.models.deletion.PROTECT, to='content.imagefile', verbose_name='image'),
        ),
    ]
