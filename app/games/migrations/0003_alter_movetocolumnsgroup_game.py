# Generated by Django 3.2.13 on 2022-04-14 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_matchtermsgame'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movetocolumnsgroup',
            name='game',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='columns', to='games.movetocolumnsgame'),
        ),
    ]
