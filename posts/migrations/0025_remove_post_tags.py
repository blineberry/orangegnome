# Generated by Django 3.0.4 on 2020-04-18 02:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_migrate_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='tags',
        ),
    ]
