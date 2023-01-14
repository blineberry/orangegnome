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
from django.utils.html import mark_safe
from django.template.loader import render_to_string

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

    image = ResizedImageField(
        size=[1188,1188], 
        quality=70, 
        upload_to=upload_to_callable,
        storage=PublicAzureStorage, 
        height_field="image_height", 
        width_field="image_width",
        keep_meta=False)
    """The Photo."""

    image_height = models.PositiveIntegerField()
    """The height of the image."""

    image_width = models.PositiveIntegerField()
    """The width of the image."""

    caption = models.CharField(max_length=560, blank=True)
    """The caption for the photo."""

    alternative_text = models.CharField(max_length=255)
    """The alternative text description of the photo."""

    html_class = 'photo'

    def __str__(self):
        return self.caption

    # From https://stackoverflow.com/a/37965068/814492
    def image_tag(self):
        """Returns html for the Admin change view to display the uploaded image."""
        if self.image is None:
            return ""

        return mark_safe('<img src="%s" style="max-width: 200px; max-height: 200px; width: auto; height: auto;" />' % (self.image.url))

    image_tag.short_description = 'Preview'


    def content_html(self):
        """Returns an html representation of the content."""
        return '<div class="photo"><img class="u-photo" src="' + self.image.url + '" alt="' + self.alternative_text + '"><p class="p-content">' + self.caption + '</p></div>'

    def get_absolute_url(self):
        """Returns the url for the photo relative to the root."""
        return reverse('photos:detail', args=[self.id])

    def feed_item_content(self):
        """Returns the content for aggregated feed item indexes."""
        return render_to_string('photos/_photo_content.html', { 'photo': self })

    def feed_item_header(self):
        return self.published

    def to_twitter_status(self):        
        """Return the content that should be the tweet status."""
        return self.caption
    
    def get_twitter_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to
    
    def has_twitter_media(self):
        """Returns True if the Model has media to upload."""
        return self.image is not None
    
    def get_twitter_media_image_field(self):
        """Returns the ImageField for the media."""
        return self.image

    def get_twitter__media_alttext(self):
        """Returns the description for the media."""
        return self.alternative_text
    
    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        return self.caption
    
    def get_mastodon_idempotency_key(self):
        """Return a string to use as the Idempotency key for Status posts."""
        return str(self.id) + str(self.updated)
    
    def get_mastodon_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to

    def get_mastodon_tags(self):
        """Return the tags that should be parsed and added to the status."""
        return self.tags.all()
    
    def has_mastodon_media(self):
        """Returns True if the Model has media to upload."""
        return self.image is not None
    
    def get_mastodon_media_image_field(self):
        """Returns the ImageField for the media."""
        return self.image

    def get_mastodon_media_description(self):
        """Returns the description for the media."""
        return self.alternative_text