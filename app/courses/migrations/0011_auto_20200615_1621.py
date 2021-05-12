# Generated by Django 3.0.7 on 2020-06-15 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_auto_20200615_1618'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ['custom_order'], 'verbose_name': 'section', 'verbose_name_plural': 'sections'},
        ),
        migrations.AlterField(
            model_name='section',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='courses.Course', verbose_name='course'),
        ),
        migrations.AlterField(
            model_name='section',
            name='create_discussions',
            field=models.BooleanField(default=False, help_text="* FOR UPLOAD SECTION ONLY *: automatically create a discussion board based on participant's video submissions.", verbose_name='create dicussion'),
        ),
        migrations.AlterField(
            model_name='section',
            name='custom_order',
            field=models.PositiveIntegerField(default=0, verbose_name='custom order'),
        ),
        migrations.AlterField(
            model_name='section',
            name='description',
            field=models.TextField(blank=True, help_text='Course description (max 800 characters)', max_length=800, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='section',
            name='name',
            field=models.CharField(help_text='Section name (max 15 characters)', max_length=15, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='section',
            name='published',
            field=models.BooleanField(default=False, verbose_name='published'),
        ),
        migrations.AlterField(
            model_name='section',
            name='requirement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sections', to='courses.Section', verbose_name='requirement'),
        ),
        migrations.AlterField(
            model_name='section',
            name='section_output',
            field=models.ForeignKey(blank=True, help_text='* FOR UPLOAD SECTION ONLY *: Define the section in which to create the discussion boards.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sections_output', to='courses.Section', verbose_name='section output'),
        ),
        migrations.AlterField(
            model_name='section',
            name='section_type',
            field=models.CharField(choices=[('D', 'Discussion boards'), ('V', 'Videos'), ('Q', 'Quizzes'), ('U', 'Uploads')], max_length=1, verbose_name='section type'),
        ),
        migrations.AlterField(
            model_name='section',
            name='show_thumbnails',
            field=models.BooleanField(default=True, help_text='* FOR VIDEO SECTION ONLY *: enables displaying video thumbnails.', verbose_name='show thumbnails'),
        ),
    ]