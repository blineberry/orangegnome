import json
from urllib.parse import urlparse
import re

import tweepy
from django.conf import settings
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models

from syndications.mastodon_client import Client as MastodonClient
import io

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
    def syndicate_to_twitter(update=None, media=None):
        api = Syndication.get_twitter_client()
        media_id = None

        if media is not None:
            media_response = api.media_upload(media.filename, file=media.file)
            print(media_response)
            media_id = media_response.media_id_string
            api.create_media_metadata(media_id, media.alt_text)

        print(media_id)
        print(update)

        response = api.update_status(update.status, in_reply_to_status_id=update.in_reply_to_status_id, attachment_url=update.attachment_url, media_ids=[media_id])
        return response

    @staticmethod
    def delete_from_twitter(id_str):
        api = Syndication.get_twitter_client()
        
        response = api.destroy_status(id_str)
        return response

    @staticmethod
    def syndicate_to_mastodon(status=None, media=None):
        if media is not None:
            response = MastodonClient.post_media(media.file, media.thumbnail, media.description, media.focus)

            if status is not None:
                status.media_ids = [response['id']]

        return MastodonClient.post_status(status.status, status.idempotency_key, status.in_reply_to_id, status.media_ids)

    @staticmethod
    def delete_from_mastodon(id):
        return MastodonClient.delete_status(id)

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

    def to_twitter_status(self):        
        """Return the content that should be the tweet status."""
        raise NotImplementedError("to_twitter_status not implemented.")
    
    def get_twitter_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        raise NotImplementedError("get_twitter_reply_to_url not implemented.")

    def to_twitter_status_update(self):
        """Converts the Note model to an object able to post to Twitter."""

        # Get the basic Twitter Status object from the content.
        update = TwitterStatusUpdate(self.to_twitter_status())

        # If Note is not replying to anything, return the update as it is.
        if self.get_twitter_reply_to_url() is None:
            return update

        # Check if the reply to url is a twitter url, if it's a twitter status,
        # parse the screen name and status id from it.
        is_twitter_url, is_twitter_status, reply_to_screen_name, reply_to_status_id = TwitterSyndicatable.parse_twitter_url(self.get_twitter_reply_to_url())

        # If the reply to url is not a twitter url and is not a twitter status,
        # append the reply to url to the end of the Note content.
        if not is_twitter_url or not is_twitter_status:
            update.status = f'{update.status} {self.in_reply_to}'
            return update

        # If the Note content starts with the reply to screen name, then it's 
        # a reply.  Add that data to the update object.
        if update.status.lower().startswith(f'@{reply_to_screen_name.lower()}'):
            update.in_reply_to_status_id = reply_to_status_id
            return update

        # Otherwise, it's a quote tweet. Add that to the update object.
        update.attachment_url = self.get_twitter_reply_to_url()
        return update
    
    def has_twitter_media(self):
        """Returns True if the Model has media to upload."""
        return False
    
    def get_twitter_media_image_field(self):
        """Returns the ImageField for the media."""
        raise NotImplementedError("get_twitter_media_image_field not implemented.")

    def get_twitter__media_alttext(self):
        """Returns the description for the media."""
        raise NotImplementedError("get_twitter__media_alttext not implemented.")

    def get_twitter_media(self):
        if not self.has_twitter_media():
            return None

        media = self.get_twitter_media_image_field()

        media_upload = TwitterMedia(media.name.split('/')[-1], file=media, alt_text=self.get_twitter__media_alttext())
        return media_upload  

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

class TwitterMedia(object):
    def __init__(self, filename, file=None, alt_text=None):
        self.filename = filename
        self.file = file
        self.alt_text = alt_text

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
#    class Meta:
#        abstract = True
#
#class PhotosSummaryPrimary(models.Model):
#    source = models.IntegerField()
#    unique_id = models.CharField(max_length=255)
#    urls = models.TextField()
#
#    class Meta:
#        abstract = True
#
#class PhotosSummary(models.Model):
#    count = models.IntegerField()
#    primary = models.OneToOneField(PhotosSummaryPrimary, on_delete=models.CASCADE)
#
#    class Meta:
#        abstract = True
#
#class SummaryGear(models.Model):
#    strava_id = models.CharField(max_length=255)
#    resource_state = models.IntegerField()
#    primary = models.BooleanField()
#    name = models.Text()
#    distance = models.FloatField()
#
#    class Meta:
#        abstract = True
#
class StravaActivity(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

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

    def get_url(self):
        return f'https://www.strava.com/activities/{self.strava_id}'

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
#    class Meta:
#        abstract = True

class StravaSyndicatable(models.Model):
    strava_activity = GenericRelation(StravaActivity)
    
    def is_syndicated_to_strava(self):
        return self.strava_activity.all().exists()

    class Meta:
        abstract = True

class StravaWebhook(models.Model):
    verify_token = models.CharField(max_length=32)
    subscription_id = models.IntegerField(null=True)

    def __str__(self):
        return 'Webhook: {}'.format(self.verify_token)

class StravaWebhookEvent(models.Model):
    object_type = models.CharField(max_length=16)
    object_id = models.BigIntegerField()
    aspect_type = models.CharField(max_length=12)
    updates = models.TextField()
    owner_id = models.BigIntegerField()
    subscription_id = models.IntegerField()
    event_time = models.BigIntegerField()

# 
# MASTODON SYNDICATION FEATURE
# 
class MastodonStatus(models.Model):
    """
    The Mastodon Status from Mastodon.
    """
    id_str = models.CharField(max_length=40)
    url = models.CharField(max_length=2048)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField()

class MastodonStatusUpdate(object):
    """
    An object to contain the necessary data to publish a Mastodon Status.
    """
    def __init__(self, status=None, idempotency_key=None, in_reply_to_id=None, tags=None, media_ids=None):
        self.status = status
        self.idempotency_key = idempotency_key
        self.in_reply_to_id = in_reply_to_id
        self.tags = tags
        self.media_ids = media_ids

class MastodonMediaUpload(object):
    """
    An object to contain the necessary data to publish a Mastodon 
    Media attachment.
    """
    def __init__(self, file, thumbnail=None, description=None, focus=None):
        self.file = file
        self.thumbnail = thumbnail
        self.description = description
        self.focus = focus


class MastodonSyndicatable(models.Model):
    """
    An abstract class to be inherited by Models that want to syndicate
    to Mastodon.
    """

    syndicated_to_mastodon = models.DateTimeField(null=True)
    syndicate_to_mastodon = models.BooleanField(default=False)
    mastodon_status = GenericRelation(MastodonStatus)
    
    def is_syndicated_to_mastodon(self):
        return self.mastodon_status.all().exists()

    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        raise NotImplementedError("to_mastodon_status not implemented.")
    
    def get_mastodon_idempotency_key(self):
        """Return a string to use as the Idempotency key for Status posts."""
        raise NotImplementedError("get_mastodon_idempotency_key not implemented.")
    
    def get_mastodon_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        raise NotImplementedError("get_mastodon_reply_to_url not implemented.")

    def get_mastodon_tags(self):
        """Return the tags that should be parsed and added to the status."""
        raise NotImplementedError("get_mastodon_tags not implemented.")
    
    def has_mastodon_media(self):
        """Returns True if the Model has media to upload."""
        return False
    
    def get_mastodon_media_image_field(self):
        """Returns the ImageField for the media."""
        raise NotImplementedError("get_mastodon_media_image_field not implemented.")

    def get_mastodon_media_description(self):
        """Returns the description for the media."""
        raise NotImplementedError("get_mastodon_media_description not implemented.")

    def get_mastodon_status_update(self):
        # Get the basic Mastodon Status object from the content.
        status = MastodonStatusUpdate(self.to_mastodon_status())

        status.idempotency_key = self.get_mastodon_idempotency_key();

        # Check the reply for a Mastodon Id.
        in_reply_to_id = MastodonSyndicatable.parse_mastodon_url(self.get_mastodon_reply_to_url())

        # If no Mastodon Id, append the reply to url to the end of the 
        # Note content.
        if self.get_mastodon_reply_to_url() is not None and in_reply_to_id is None:
            status.status = f'{self.content}\n\n{self.in_reply_to}'
        # Otherwise add the reply_to_id
        elif self.get_mastodon_reply_to_url() is not None and in_reply_to_id is not None:
            status.in_reply_to_id = in_reply_to_id
            
        status.status = MastodonSyndicatable.add_hashtags(status.status, self.get_mastodon_tags())
        
        return status

    def get_mastodon_media_upload(self):
        if not self.has_mastodon_media():
            return None

        media = self.get_mastodon_media_image_field()
        # https://stackoverflow.com/a/35974071/814492
        file = (media.name.split('/')[-1], media)

        media_upload = MastodonMediaUpload(file, description=self.get_mastodon_media_description())
        return media_upload

    @staticmethod
    def parse_mastodon_url(url):
        o = urlparse(url)

        if o.netloc.lower() != settings.MASTODON_INSTANCE.lower():
            return None

        pieces = o.path.split("/")
        if len(pieces) < 3:
            return None        
        
        mastodonUserPattern = re.compile("^@(.+)$")
        mastodonStatusIdPattern = re.compile("^(.+)$")

        if bool(mastodonUserPattern.match(pieces[1])) and bool(mastodonStatusIdPattern.match(pieces[2])):            
            return pieces[2]

        return None
    
    @staticmethod
    def add_hashtags(status, tags):
        tagsToAppend = list()

        for tag in tags:
            tagPattern = re.compile(r"\b(%s)\b" % tag.name, re.IGNORECASE)
            
            if bool(tagPattern.search(status)):
                status = tagPattern.sub(tag.to_hashtag(), status, 1)
                continue

            tagsToAppend.append(tag.to_hashtag())

        if len(tagsToAppend) > 0:
            status += "\n\n"
            status += " ".join(tagsToAppend)

        return status


    class Meta:
        abstract = True