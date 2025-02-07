# Generated by Django 4.2.18 on 2025-02-05 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0012_data_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookmark',
            name='commentary_html',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='quote_html',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='bookmark',
            name='title_html',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='commentary_md',
            field=models.TextField(blank=True, help_text='CommonMark supported.', verbose_name='commentary'),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='commentary_txt',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='quote_md',
            field=models.TextField(blank=True, help_text='CommonMark supported.', verbose_name='quote'),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='quote_txt',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='title_md',
            field=models.TextField(blank=True, help_text='CommonMark supported. Inline elements only.', verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='bookmark',
            name='title_txt',
            field=models.TextField(blank=True),
        ),
    ]
