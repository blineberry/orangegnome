# Generated by Django 3.0.7 on 2020-06-22 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('syndications', '0011_stravawebhook'),
    ]

    operations = [
        migrations.CreateModel(
            name='StravaWebhookEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_type', models.CharField(max_length=16)),
                ('object_id', models.BigIntegerField()),
                ('aspect_type', models.CharField(max_length=12)),
                ('updates', models.TextField()),
                ('owner_id', models.BigIntegerField()),
                ('subscription_id', models.IntegerField()),
                ('event_time', models.BigIntegerField()),
            ],
        ),
    ]
