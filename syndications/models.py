from typing import Any, Dict, Tuple
from urllib.parse import urlparse
import re

import tweepy
from django.conf import settings
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.db import models

from syndications.mastodon_client import Client as MastodonClient
from django.db.models import UniqueConstraint
import bleach
from webmentions.models import OutgoingContent
from django.urls import reverse

# Create your models here.
class Syndication():
    name = models.TextField(max_length=50)
    url = models.TextField(max_length=2000)

    @staticmethod
    def get_twitter_v2_client():
        return tweepy.Client(
            consumer_key=settings.TWITTER_CONSUMER_KEY, 
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN_KEY,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )

    @staticmethod
    def get_twitter_v1_client():
        auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
        auth.set_access_token(settings.TWITTER_ACCESS_TOKEN_KEY, settings.TWITTER_ACCESS_TOKEN_SECRET)
        
        return tweepy.API(auth)

    @staticmethod
    def syndicate_to_twitter(update=None, media=None):
        client = Syndication.get_twitter_v2_client()
        media_ids = None

        if media is not None:
            api = Syndication.get_twitter_v1_client()
            media_response = api.media_upload(media.filename, file=media.file)
            media_id = media_response.media_id_string
            api.create_media_metadata(media_id, media.alt_text)

            media_ids = [media_id]

        response = client.create_tweet(text=update.status, in_reply_to_tweet_id=update.in_reply_to_status_id, media_ids=media_ids, user_auth=True)
        return response

    @staticmethod
    def delete_from_twitter(id_str):
        client = Syndication.get_twitter_v2_client()
        
        response = client.delete_tweet(id_str, user_auth=True)
        return response

    @staticmethod
    def syndicate_to_mastodon(status=None, media=None):
        if media is not None:
            response = MastodonClient.post_media(media.file, media.thumbnail, media.description, media.focus)

            if status is not None:
                status.media_ids = [response['id']]

        return MastodonClient.post_status(status.status, status.idempotency_key, status.in_reply_to_id, status.media_ids)
    
    @staticmethod
    def favorite_on_mastodon(id=None):
        if id is None:
            return
        
        return MastodonClient.favorite_status(id)
    
    @staticmethod
    def unfavorite_on_mastodon(id=None):
        if id is None:
            return
        
        return MastodonClient.unfavorite_status(id)
    
    @staticmethod
    def boost_on_mastodon(id=None):
        if id is None:
            return
        
        return MastodonClient.boost_status(id)
    
    @staticmethod
    def unboost_on_mastodon(id=None):
        if id is None:
            return
        
        return MastodonClient.unboost_status(id)

    @staticmethod
    def delete_from_mastodon(id):
        return MastodonClient.delete_status(id)
    
    @staticmethod
    def update_mastodon_replies(id):
        status = MastodonStatus.objects.filter(id_str=id).first()

        if status is None:
            replies = MastodonReply.objects.filter(in_reply_to_id_str=id)
            for reply in replies:
                reply.delete()
            return

        context = MastodonClient.get_status_context(id)

        if context is None:
            return
        
        if context.get("descendants") is None:
            replies = MastodonReply.objects.filter(in_reply_to_id_str=id)
            for reply in replies:
                reply.delete()
            return
        
        processed_ids = []
        
        for descendent in context["descendants"]:
            if descendent.get("in_reply_to_id") != id:
                continue

            descendent_status = MastodonClient.get_status(descendent.get("id"))

            content = descendent_status["content"]
            content = bleach.clean(content, tags=bleach.sanitizer.ALLOWED_TAGS.union(('p', 'br')))
            content = bleach.linkify(content)

            MastodonReply.objects.update_or_create(
                id_str=descendent_status["id"],                 
                defaults={
                    'in_reply_to_id_str':descendent_status["in_reply_to_id"],
                    'content':content,
                    'author_name':descendent_status["account"].get("display_name"),
                    'author_url':descendent_status["account"].get("url"),
                    'author_photo':descendent_status["account"].get("avatar_static"),
                    'published':descendent_status["created_at"],
                    'url':descendent_status["url"],
                    'reply_to_url':status.content_object.get_permalink()
                }                
            )

            processed_ids.append(descendent_status["id"])

        replies = MastodonReply.objects.filter(in_reply_to_id_str=status.id_str).exclude(id_str__in=processed_ids)
        for reply in replies:
            reply.delete()

    @staticmethod
    def update_mastodon_boosts(id):
        status = MastodonStatus.objects.filter(id_str=id).first()

        if status is None:
            boosts = MastodonBoost.objects.filter(boost_of_id_str=status.id_str)
            for boost in boosts:
                boost.delete()
            return

        accounts = MastodonClient.get_status_boost_accounts_all(id)

        if accounts is None:
            boosts = MastodonBoost.objects.filter(boost_of_id_str=status.id_str)
            for boost in boosts:
                boost.delete()
            return
                
        processed_ids = []
        
        for account in accounts:
            boost = MastodonBoost.objects.update_or_create(
                account_id_str=account["id"],
                url=status.url,
                author_name=account["display_name"],
                author_url=account["url"],
                author_photo=account["avatar_static"],
                boost_of_id_str=status.id_str,
                repost_of_url=status.content_object.get_permalink()
            )[0]

            boost_status = MastodonClient.get_account_status_by_reblog_of_id(id=boost.repost_of_url, account_id=boost.account_id_str)

            if boost_status is None:
                return
            
            boost.published = boost_status.get("created_at")        

            processed_ids.append(account["id"])

        boosts = MastodonBoost.objects.filter(boost_of_id_str=status.id_str).exclude(account_id_str__in=processed_ids)
        for boost in boosts:
            boost.delete()

    @staticmethod
    def update_mastodon_favourites(id):
        status = MastodonStatus.objects.filter(id_str=id).first()

        if status is None:
            favourites = MastodonFavourite.objects.filter(like_of_url=status.id_str)
            for favourite in favourites:
                favourite.delete()
            return

        accounts = MastodonClient.get_status_favorite_accounts_all(id)

        if accounts is None:
            favourites = MastodonFavourite.objects.filter(like_of_url=status.id_str)
            for favourite in favourites:
                favourite.delete()
            return
        
        processed_ids = []

        for account in accounts:
            MastodonFavourite.objects.update_or_create(
                account_id_str=account["id"],
                url=status.url,
                author_name=account["display_name"],
                author_url=account["url"],
                author_photo=account["avatar_static"],
                favourite_of_id_str=status.id_str,
                like_of_url=status.content_object.get_permalink()
            )     

            processed_ids.append(account["id"])

        favourites = MastodonFavourite.objects.all().filter(favourite_of_id_str=status.id_str).exclude(account_id_str__in=processed_ids)

        for favourite in favourites:
            favourite.delete()

    class Meta:
        abstract = True

class TwitterUser(models.Model):
    id_str = models.CharField(max_length=40,primary_key=True)
    name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=30)

class Tweet(models.Model):
    id_str = models.CharField(max_length=40)
    created_at = models.DateTimeField(null=True)
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
    tweet_length_limit = 280
    tweet_link_length = 23

    def get_tweet_datetime(self):
        tweet_created_at = self.tweet.get().created_at

        if tweet_created_at is not None:
            return tweet_created_at
        
        return self.syndicated_to_twitter
    
    def is_syndicated_to_twitter(self):
        return self.tweet.all().exists()

    def to_twitter_status(self):        
        """Return the content that should be the tweet status."""
        raise NotImplementedError("to_twitter_status not implemented.")
    
    def get_twitter_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        raise NotImplementedError("get_twitter_reply_to_url not implemented.")

    def to_twitter_status_update(self):
        """Converts the model to an object able to post to Twitter."""

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

        # Otherwise it's a reply. Add that data to the update object.
        update.in_reply_to_status_id = reply_to_status_id
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

    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)
        
        MastodonStatusesToProcess.objects.get_or_create(self.id_str)

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
    mastodon_status = GenericRelation(MastodonStatus, related_query_name="mastodon_status")
    
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
    
    def is_mastodon_favorite(self):
        """Returns True if the interaction is a boost."""
        return False
    
    def is_mastodon_boost(self):
        """Returns True if the interaction is a boost."""
        return False
    
    def is_mastodon_url(self, url):
        o = urlparse(url)

        return o.netloc == "mastodon.online"
    
    def get_mastodon_url(self):
        raise NotImplementedError("get_mastodon_url not implemented.")
    
    def get_status_id_from_url(self):
        url = self.get_mastodon_url()

        if not url:
            return None
        
        if not self.is_mastodon_url(url):
            return None
        
        o = urlparse(url)

        path_parts = o.path.split("/")

        if len(path_parts) != 3:
            return None
        
        return path_parts[2]

    def get_mastodon_media_image_field(self):
        """Returns the ImageField for the media."""
        raise NotImplementedError("get_mastodon_media_image_field not implemented.")

    def get_mastodon_media_description(self):
        """Returns the description for the media."""
        raise NotImplementedError("get_mastodon_media_description not implemented.")

    def get_mastodon_status_update(self):
        # Get the basic Mastodon Status object from the content.
        status = MastodonStatusUpdate(self.to_mastodon_status())

        status.idempotency_key = self.get_mastodon_idempotency_key()

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
            tagsToAppend.append(tag.to_hashtag())

        if len(tagsToAppend) > 0:
            status += "\n\n"
            status += " ".join(tagsToAppend)

        return status


    class Meta:
        abstract = True

class Reply(models.Model):
    title = models.CharField(max_length=64, null=True, blank=True)
    reply_to_url = models.URLField()
    content = models.TextField()
    author_name = models.CharField(max_length=100, null=True, blank=True)
    author_url = models.URLField(null=True, blank=True)
    author_photo = models.URLField(null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    url = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)

class Repost(models.Model):
    repost_of_url = models.URLField()
    author_name = models.CharField(max_length=100, null=True, blank=True)
    author_url = models.URLField(null=True, blank=True)
    author_photo = models.URLField(null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    url = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)

class Like(models.Model):
    like_of_url = models.URLField()
    author_name = models.CharField(max_length=100, null=True, blank=True)
    author_url = models.URLField(null=True, blank=True)
    author_photo = models.URLField(null=True, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    url = models.URLField()
    updated_at = models.DateTimeField(auto_now=True)

class MastodonReply(Reply):
    id_str = models.CharField(max_length=40)
    in_reply_to_id_str = models.CharField(max_length=40)
    
    def get_permalink(self):
        return settings.SITE_URL + reverse('syndications:reply', args=[self.id])

    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:
        permalink = self.get_permalink()
        super().delete(*args, **kwargs)
        OutgoingContent.objects.get_or_create(content_url=permalink)

    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        
        permalink = settings.SITE_URL + reverse('syndications:reply', args=[self.id])
        OutgoingContent.objects.get_or_create(content_url=permalink)
        MastodonStatusesToProcess.objects.get_or_create(id_str=self.in_reply_to_id_str)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("id_str",),
                name="unique_mastodon_id",
            ),
        ]

class MastodonBoost(Repost):
    account_id_str = models.CharField(max_length=40)
    boost_of_id_str = models.CharField(max_length=40)
    
    def get_permalink(self):
        return settings.SITE_URL + reverse('syndications:repost', args=[self.id])

    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:
        permalink = self.get_permalink()
        super().delete(*args, **kwargs)
        OutgoingContent.objects.get_or_create(content_url=permalink)

    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        
        permalink = settings.SITE_URL + reverse('syndications:repost', args=[self.id])
        OutgoingContent.objects.get_or_create(content_url=permalink)
        MastodonStatusesToProcess.objects.get_or_create(id_str=self.boost_of_id_str)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("account_id_str", "boost_of_id_str"),
                name="unique_mastodon_account_id_str_boost_of_id_str",
            ),
        ]

class MastodonFavourite(Like):
    account_id_str = models.CharField(max_length=40)
    favourite_of_id_str = models.CharField(max_length=40)

    def get_permalink(self):
        return settings.SITE_URL + reverse('syndications:like', args=[self.id])

    def delete(self, *args, **kwargs) -> Tuple[int, Dict[str, int]]:
        permalink = self.get_permalink()
        super().delete(*args, **kwargs)
        OutgoingContent.objects.get_or_create(content_url=permalink)

    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        
        permalink = self.get_permalink()
        OutgoingContent.objects.get_or_create(content_url=permalink)
        MastodonStatusesToProcess.objects.get_or_create(id_str=self.favourite_of_id_str)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("account_id_str", "favourite_of_id_str"),
                name="unique_mastodon_account_id_str_favourite_of_id_str",
            ),
        ]

class MastodonStatusesToProcess(models.Model):
    id_str = models.CharField(max_length=40)
    result = models.TextField()

    def __str__(self) -> str:
        return self.id_str

    def process(self):
        try:
            Syndication.update_mastodon_replies(self.id_str)
            Syndication.update_mastodon_boosts(self.id_str)
            Syndication.update_mastodon_favourites(self.id_str)

            self.delete()
        except Exception as e:
            self.result = str(e)
            self.save()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=("id_str",),
                name="unique_mastodon_id_str",
            ),
        ]