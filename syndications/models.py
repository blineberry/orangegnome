from django.db import models
import tweepy
from django.conf import settings
import json
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from urllib.parse import urlparse

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
    def syndicate_to_twitter(status, in_reply_to_status_id=None, attachment_url=None):
        api = Syndication.get_twitter_client()

        response = api.update_status(status, in_reply_to_status_id=in_reply_to_status_id, attachment_url=attachment_url, tweet_mode="extended")
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
    id_str = models.CharField(max_length=40,primary_key=True)
    name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=30)

class Tweet(models.Model):
    id_str = models.CharField(max_length=40)
    created_at = models.DateTimeField()
    screen_name = models.CharField(max_length=30)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    full_text = models.CharField(max_length=560, null=True)
    user = models.ForeignKey(TwitterUser, on_delete=models.PROTECT, related_name='tweets', null=True)
    in_reply_to_status_id_str=models.CharField(max_length=40, blank=True, null=True)
    in_reply_to_screen_name=models.CharField(max_length=100, blank=True, null=True)

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

    def to_twitter_status_update(self):
        pass

    @staticmethod
    def parse_twitter_url(url):
        o = urlparse(url)

        if o.netloc != 'twitter.com':
            return False, False, None, None

        pieces = o.path.split("/")

        if len(pieces) < 4:
            return True, False, None, None

        if pieces[2].lower() != 'status':
            return True, False, None, None
        
        return True, True, pieces[1], pieces[3]

    class Meta:
        abstract = True

class TwitterStatusUpdate(object):
    def __init__(self, status=None, in_reply_to_status_id=None, attachment_url=None):
        self.status = status
        self.in_reply_to_status_id = in_reply_to_status_id
        self.attachment_url = attachment_url

#class StravaLatLng(models.Model):
#    lat = models.FloatField()
#    lng = models.FloatField()
#
#    class Meta:
#        abstract = True
#
#class StravaPolylineMap(models.Model):
#    polyline = models.Text()
#    summary_polyline = models.Text()
#
#    class Mega:
#        abstract = True
#
#class PhotosSummaryPrimary(models.Model):
#    source = models.IntegerField()
#    unique_id = models.CharField(max_length=255)
#    urls = models.TextField()
#
#    class Mega:
#        abstract = True
#
#class PhotosSummary(models.Model):
#    count = models.IntegerField()
#    primary = models.OneToOneField(PhotosSummaryPrimary, on_delete=models.CASCADE)
#
#    class Mega:
#        abstract = True
#
#class SummaryGear(models.Model):
#    strava_id = models.CharField(max_length=255)
#    resource_state = models.IntegerField()
#    primary = models.BooleanField()
#    name = models.Text()
#    distance = models.FloatField()
#
#    class Mega:
#        abstract = True
#
class StravaActivity(models.Model):
    strava_id = models.BigIntegerField()
    #external_id = models.CharField(max_length=255)
    #upload_id = models.BigIntegerField()
    athlete = models.IntegerField()
    #name = models.Text()
    distance = models.FloatField()
    moving_time = models.IntegerField()
    elapsed_time = models.IntegerField()
    total_elevation_gain = models.FloatField()
    #elev_high = models.FloatField()
    #elev_high = models.FloatField()
    type = models.CharField(max_length=30)
    start_date = models.DateTimeField()
    start_date_local = models.DateTimeField()
    timezone = models.CharField(max_length=50)
    #start_latlng = models.OneToOneField(StravaLatLng, on_delete=models.CASCADE)
    #end_latlng = models.OneToOneField(StravaLatLng, on_delete=models.CASCADE)
    #achievement_count = models.IntegerField()
    #kudos_count = models.IntegerField()
    #comment_count = models.IntegerField()
    #athlete_count = models.IntegerField()
    #photo_count = models.IntegerField()
    #total_photo_count = models.IntegerField()
    #map = models.OneToOneField(StravaPolylineMap, on_delete=models.CASCADE)
    #trainer = models.BooleanField()
    #commute = models.BooleanField()
    #manual = models.BooleanField()
    private = models.BooleanField()
    #flagged = models.BooleanField()
    #workout_type = models.IntegerField()
    #upload_id_str = models.CharField(max_length=128)
    #average_speed = models.FloatField()
    #max_speed = models.FloatField()
    #has_kudoed = models.BooleanField()
    #gear_id = models.CharField(255)
    #kilojoules = models.FloatField()
    #average_watts = models.FloatField()
    #device_watts = models.BooleanField()
    #max_watts = models.IntegerField()
    #weighted_average_watts = models.IntegerField()
    #description = models.TextField(null=True)
    #photos = models.OneToOneField(StravaPhotosSummary, on_delete=models.CASCADE)
    #gear = models.ForeignKey(SummaryGear)
    #calories = models.FloatField()

    class Mega:
        abstract = True

#class DetailedSegmentEfford(models.Model):
#    strava_id = models.BigIntegerField()
#    elapsed_time = models.IntegerField()
#    start_date = models.DateTimeField()
#    start_date_local = models.DateTimeField()
#    distance = models.FloatField()
#    is_kom = models.BooleanField()
#    name = models.TextField()
#    activity = models.ForeignKey(StravaActivity, on_delete=models.CASCADE)
#    athlete = models.IntegerField()
#    moving_time = models.IntegerField()
#    start_index = models.IntegerField()
#    end_index = models.IntegerField()
#    average_cadence = models.FloatField()
#    average_watts = models.FloatField()
#    device_watts = models.BooleanField()
#    average_heartrate = models.FloatField()
#    max_heartrate = models.FloatField()
#
#    class Mega:
#        abstract = True