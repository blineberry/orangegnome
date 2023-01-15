"""

"""

from django.db import models
from profiles.models import Profile
from feed.models import Tag, FeedItem
from syndications.models import TwitterSyndicatable, TwitterStatusUpdate, MastodonSyndicatable, MastodonStatusUpdate
from django.urls import reverse
from urllib.parse import urlparse
import re

# An indieweb "Note" contenttype https://indieweb.org/note
class Note(MastodonSyndicatable, TwitterSyndicatable, FeedItem):
    """
    A Note model.

    Implements MastodonSyndicatable, TwitterSyndicatable, and FeedItem.
    """
    content = models.CharField(max_length=560)
    """The Note content. Max length is 560 characters."""

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        """Returns the url for the note relative to the root."""
        return reverse('notes:detail', args=[self.id])

    def feed_item_content(self):
        """Returns the content for aggregated feed item indexes."""
        return self.content_html()

    @staticmethod
    def doublespaces_to_paragraphs(content):
        """
        Returns the passed in content with doublespaces converted to html `p` 
        elements.
        """

        # Standardize End Of Lines to Line Feeds
        content = re.sub(r"(\r\n)", "\n", content)
        # Standardize Carriage Returns to Line Feeds
        content = re.sub(r"(\r)", "\n", content)
        # Convert 2+ Line Feeds to paragraph elements
        content = re.sub(r"\n{2,}", "<p>", content)
        # Convert remaining Line Feeds to line break elements
        content = re.sub(r"\n", "<br>", content)
        return content

    @staticmethod
    def urls_to_links(content, target="_blank"):
        """
        Returns the passed in content with links converted to html `a` 
        elements.
        """
        # Taken from https://gist.github.com/guillaumepiot/4539986
        # Replace url to link
        anchorRepl = r'<a href="\1" target="' + target + r'">\1</a>'
        urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE|re.UNICODE)
        content = urls.sub(anchorRepl, content)
        return content

    def content_html(self):
        """Returns the content with specific html conversions."""
        return '<p>' + Note.urls_to_links(Note.doublespaces_to_paragraphs(self.content), "_self")

    def feed_item_header(self):
        """Returns the title for aggregated feed item indexes."""
        return self.published

    def to_twitter_status(self):        
        """Return the content that should be the tweet status."""
        return self.content
    
    def get_twitter_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to
    
    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        return self.content
    
    def get_mastodon_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to

    def get_mastodon_tags(self):
        """Return the tags that should be parsed and added to the status."""
        return self.tags.all()
    
    def get_mastodon_idempotency_key(self):
        """Return a string to use as the Idempotency key for Status posts."""
        return str(self.id) + str(self.updated)