# Generated by Django 3.0.3 on 2020-04-12 18:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0019_likertattempt'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenEnded',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='quiz.Question')),
            ],
            options={
                'verbose_name': 'open ended question',
                'verbose_name_plural': 'open ended questions',
            },
            bases=('quiz.question',),
        ),
        migrations.CreateModel(
            name='OpenEndedAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('answer', models.TextField(blank=True, null=True, verbose_name='answer')),
                ('no_of_attempt', models.PositiveIntegerField(default=1)),
                ('openended', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='quiz.OpenEnded')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'open ended attempt',
                'verbose_name_plural': 'open ended attempts',
            },
        ),
    ]
