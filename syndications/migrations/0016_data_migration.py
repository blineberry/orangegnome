from django.db import migrations, models
import django.db.models.deletion
from django.contrib.contenttypes.models import ContentType

def get_twitter_url(screen_name, user, id_str):

    if user is not None:
        screen_name = user.screen_name

    return f'https://twitter.com/{screen_name}/status/{id_str}'

def forwards_func(apps, schema_editor):
    MastodonStatus = apps.get_model("syndications", "MastodonStatus")
    Tweet = apps.get_model("syndications", "Tweet")
    FeedSyndication = apps.get_model("feed", "Syndication")
    db_alias = schema_editor.connection.alias

    for mastodonStatus in MastodonStatus.objects.using(db_alias).filter(syndication_id=None):
        ct = ContentType.objects.using(db_alias).get(pk=mastodonStatus.content_type_id)

        model = apps.get_model(ct.app_label, ct.model)
        o = model.objects.using(db_alias).get(pk=mastodonStatus.object_id)

        fs = FeedSyndication.objects.using(db_alias).create(name="Mastodon", url=mastodonStatus.url, syndicated_post_id=o.feeditem_ptr_id)
        mastodonStatus.syndication_id=fs.id
        mastodonStatus.save()
    
    for tweet in Tweet.objects.using(db_alias).filter(syndication_id=None):
        ct = ContentType.objects.using(db_alias).get(pk=tweet.content_type_id)

        model = apps.get_model(ct.app_label, ct.model)
        o = model.objects.using(db_alias).get(pk=tweet.object_id)

        print({
            "tweet": {
                "__str__": tweet,
                "id": tweet.id,
                "id_str": tweet.id_str
            }
        })

        fs = FeedSyndication.objects.using(db_alias).create(name="Twitter", url=get_twitter_url(tweet.screen_name, tweet.user, tweet.id_str), syndicated_post_id=o.feeditem_ptr_id)
        tweet.syndication_id=fs.id
        tweet.save()

def reverse_func(apps, schema_editor):
    MastodonStatus = apps.get_model("syndications", "MastodonStatus")
    Tweet = apps.get_model("syndications", "Tweet")
    Syndication = apps.get_model("syndications", "Syndication")
    FeedSyndication = apps.get_model("feed", "Syndication")
    db_alias = schema_editor.connection.alias

    for mastodonStatus in MastodonStatus.objects.using(db_alias).exclude(syndication_id=None):
        mastodonStatus.syndication_id = None
        mastodonStatus.save()

    for tweet in Tweet.objects.using(db_alias).exclude(syndication_id=None):
        tweet.syndication_id = None
        tweet.save()

    Syndication.objects.using(db_alias).all().delete()
    FeedSyndication.objects.using(db_alias).all().delete()

class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('syndications', '0015_syndication_mastodonstatus_syndication_and_more')
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]