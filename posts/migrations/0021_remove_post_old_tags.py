# Generated by Django 3.0.4 on 2020-04-17 02:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0020_migrate_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='old_tags',
        ),
    ]