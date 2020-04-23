from django.db import models
import tweepy
from django.conf import settings
import json
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Syndication():
    name = models.TextField(max_length=50)
    url = models.TextField(max_length=2000)

    @staticmethod
    def get_twitter_client():
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN_KEY, settings.TWITTER_ACCESS_TOKEN_SECRET)
        
        return tweepy.API(auth)

    @staticmethod
    def syndicate_to_twitter(content):
        api = Syndication.get_twitter_client()

        response = api.update_status(content, tweet_mode="extended")
        print(response)
        return response

    @staticmethod
    def delete_from_twitter(id_str):
        api = Syndication.get_twitter_client()
        
        response = api.destroy_status(id_str)
        return response

    class Meta:
        abstract = True


class TwitterUser(models.Model):
    id_str = models.TextField(max_length=40,primary_key=True)
    name = models.TextField(max_length=100)
    screen_name = models.TextField(max_length=30)

class Tweet(models.Model):
    id_str = models.CharField(max_length=40)
    created_at = models.DateTimeField()
    screen_name = models.CharField(max_length=30)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    full_text = models.CharField(max_length=560, null=True)
    user = models.ForeignKey(TwitterUser, on_delete=models.PROTECT, related_name='tweets', null=True)

    def get_url(self):
        screen_name = self.screen_name

        if self.user is not None:
            screen_name = self.user.screen_name

        return f'https://twitter.com/{screen_name}/status/{self.id_str}'

    def to_syndication(self):
        return Syndication(name='Twitter',url=self.get_url())

class TwitterSyndicatable(models.Model):
    syndicated_to_twitter = models.DateTimeField(null=True)
    syndicate_to_twitter = models.BooleanField(default=False)
    tweet = GenericRelation(Tweet)
    
    def is_syndicated_to_twitter(self):
        return self.tweet.all().exists()

    def to_twitter_status(self):
        pass

    class Meta:
        abstract = True

