# Generated by Django 3.0.4 on 2020-04-18 02:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0007_migrate_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='tags',
        ),
    ]
