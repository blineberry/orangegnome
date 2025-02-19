# Generated by Django 3.0.4 on 2020-05-06 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('feed', '0007_feeditem_in_reply_to'),
        ('profiles', '0001_squashed_0002_profile_twitter_screenname'),
        ('syndications', '0001_squashed_0016_data_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('feeditem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='feed.FeedItem')),
                ('type', models.CharField(max_length=30)),
                ('distance', models.FloatField()),
                ('moving_time', models.IntegerField()),
                ('total_elevation_gain', models.FloatField()),
                ('start_date', models.DateTimeField()),
                ('start_date_local', models.DateTimeField()),
                ('timezone', models.CharField(max_length=50)),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile')),
                ('strava_activity', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='syndications.StravaActivity')),
            ],
            bases=('feed.feeditem',),
        ),
    ]
