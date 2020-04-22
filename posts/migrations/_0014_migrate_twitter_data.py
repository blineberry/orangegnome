# Generated by Django 3.0.4 on 2020-04-01 17:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


post_app_label = 'posts'
post_model = 'TwitterSyndication'
tweet_app_label = 'syndications'
tweet_model = 'Tweet'

def migrate_data(apps, schema_editor):
    TwitterSyndication = apps.get_model(post_app_label, post_model)
    Tweet = apps.get_model(tweet_app_label, tweet_model)
    ContentType = apps.get_model('django','ContentType')

    twitterSyndicationContentType = ContentType.objects.get(app_label=post_app_label,model=post_model)

    for twitterSyndication in TwitterSyndication.objects.all():
        t = Tweet(
            id_str=twitterSyndication.id_str,
            created_at=twitterSyndication.created_at,
            screen_name=twitterSyndication.screen_name,
            object_id=twitterSyndication.post_id,
            content_type_id=twitterSyndicationContentType.id,
        )
        t.save()

def unmigrate_data(apps, schema_editor):
    TwitterSyndication = apps.get_model(post_app_label, post_model)
    Tweet = apps.get_model(tweet_app_label, tweet_model)
    
    for tweet in Tweet.objects.all():
        ts = TwitterSyndication(
            id_str=twitterSyndication.id_str,
            created_at=twitterSyndication.created_at,
            screen_name=twitterSyndication.screen_name,
            post_id=tweet.object_id
        )
        ts.save()

class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20200401_1101'),
        ('syndications', '0001_initial')
    ]

    operations = [
        migrations.RunPython(migrate_data, unmigrate_data),
    ]
