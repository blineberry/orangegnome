# Generated by Django 4.2.3 on 2023-08-31 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syndications', '0013_mastodonnotification'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MastodonNotification',
            new_name='MastodonPush',
        ),
    ]