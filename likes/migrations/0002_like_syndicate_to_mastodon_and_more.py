# Generated by Django 4.2.3 on 2023-08-21 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('likes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='syndicate_to_mastodon',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='like',
            name='syndicated_to_mastodon',
            field=models.DateTimeField(null=True),
        ),
    ]