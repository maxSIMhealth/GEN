# Generated by Django 3.1.8 on 2021-05-25 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_matchcolumn_matchcolumnsgame_matchcolumnsitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MatchColumn',
        ),
    ]