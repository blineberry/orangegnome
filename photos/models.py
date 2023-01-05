"""
Implementation of the IndieWeb Photo post type.
https://indieweb.org/photo
"""

from django.db import models
from feed.models import FeedItem
from syndications.models import TwitterSyndicatable, TwitterStatusUpdate, MastodonSyndicatable, MastodonStatusUpdate
from django.urls import reverse
from .storage import PublicAzureStorage
from uuid import uuid4
from datetime import date
from django_resized import ResizedImageField

# Custom upload_to callable
# Heavily influenced from https://stackoverflow.com/a/15141228/814492
def upload_to_callable(instance, filename):
    ext = filename.split('.')[-1]

    filename = '{}.{}'.format(uuid4().hex, ext)

    d = date.today()

    return '{0}/{1}'.format(d.strftime('%Y/%m/%d'),filename)

# Create your models here.
class Photo(MastodonSyndicatable, TwitterSyndicatable, FeedItem):
    """
    A Photo model.

    Implements MastodonSyndicatable, TwitterSyndicatable, and FeedItem.
    """
    content = ResizedImageField(size=[1188,1188], quality=70, upload_to=upload_to_callable,storage=PublicAzureStorage)
    """The Photo."""

    caption = models.TextField()
    """The caption for the photo."""

    alternative_text = models.CharField(max_length=255)
    """The alternative text description of the photo."""

    def __str__(self):
        return self.alternative_text

    def get_absolute_url(self):
        """Returns the url for the photo relative to the root."""
        return reverse('photos:detail', args=[self.id])

    def feed_item_content(self):
        """Returns the content for aggregated feed item indexes."""
        # TODO
        pass

    def feed_item_header(self):
        # TODO
        pass

    def to_twitter_status_update(self):
        # TODO 
        pass
    
    def to_mastodon_status_update(self):
        # TODO 
        pass