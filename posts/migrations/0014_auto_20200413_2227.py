# Generated by Django 3.0.4 on 2020-04-14 02:27

from django.db import migrations

post_app_label = 'posts'
post_model = 'TwitterSyndication'
tweet_app_label = 'syndications'
tweet_model = 'Tweet'

def migrate_data(apps, schema_editor):
    TwitterSyndication = apps.get_model(post_app_label, post_model)
    Tweet = apps.get_model(tweet_app_label, tweet_model)
    ContentType = apps.get_model('contenttypes','ContentType')

    twitterSyndicationContentType = ContentType.objects.get(app_label=post_app_label,model=post_model.lower())

    for twitterSyndication in TwitterSyndication.objects.all():
        t = Tweet(
            id_str=twitterSyndication.id_str,
            created_at=twitterSyndication.created_at,
            screen_name=twitterSyndication.screen_name,
            object_id=twitterSyndication.post_id,
            content_type_id=twitterSyndicationContentType.id,
        )
        t.save()

        twitterSyndication.delete()

def unmigrate_data(apps, schema_editor):
    TwitterSyndication = apps.get_model(post_app_label, post_model)
    Tweet = apps.get_model(tweet_app_label, tweet_model)
    
    for tweet in Tweet.objects.all():
        ts = TwitterSyndication(
            id_str=tweet.id_str,
            created_at=tweet.created_at,
            screen_name=tweet.screen_name,
            post_id=tweet.object_id
        )
        ts.save()

        tweet.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20200401_1332'),
        ('syndications', '0001_initial')
    ]

    operations = [
        migrations.RunPython(migrate_data, unmigrate_data),
    ]
