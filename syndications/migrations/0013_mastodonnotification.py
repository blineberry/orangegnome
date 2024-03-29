# Generated by Django 4.2.3 on 2023-08-31 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syndications', '0012_remove_mastodonpushsubscription_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MastodonNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=50, null=True)),
                ('body', models.TextField(null=True)),
                ('icon', models.URLField(null=True)),
                ('notification_id', models.CharField(max_length=40, null=True)),
                ('notification_type', models.CharField(max_length=10, null=True)),
                ('preferred_local', models.CharField(max_length=100, null=True)),
                ('title', models.CharField(max_length=200, null=True)),
                ('result', models.TextField(null=True)),
            ],
        ),
    ]
