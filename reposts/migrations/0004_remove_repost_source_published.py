# Generated by Django 4.2.3 on 2023-08-22 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reposts', '0003_repost_source_name_repost_source_published'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='repost',
            name='source_published',
        ),
    ]
