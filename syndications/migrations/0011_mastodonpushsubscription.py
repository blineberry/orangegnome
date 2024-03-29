# Generated by Django 4.2.3 on 2023-08-31 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syndications', '0010_like_created_at_reply_created_at_repost_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='MastodonPushSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privkey', models.CharField(max_length=100)),
                ('auth', models.BinaryField()),
                ('foreign_id', models.IntegerField()),
                ('endpoint', models.URLField()),
                ('alerts', models.JSONField()),
                ('server_key', models.CharField(max_length=100)),
                ('policy', models.CharField(max_length=10)),
            ],
        ),
    ]
