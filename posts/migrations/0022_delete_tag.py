# Generated by Django 3.0.4 on 2020-04-17 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_remove_post_old_tags'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Tag',
        ),
    ]
