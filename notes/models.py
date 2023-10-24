"""

"""

from django.db import models
from feed.models import FeedItem
from syndications.models import TwitterSyndicatable, MastodonSyndicatable
from django.urls import reverse
from django.utils import timezone
import mistune

# An indieweb "Note" contenttype https://indieweb.org/note
class Note(MastodonSyndicatable, TwitterSyndicatable, FeedItem):
    """
    A Note model.

    Implements MastodonSyndicatable, TwitterSyndicatable, and FeedItem.
    """
    content = models.CharField(max_length=560, help_text="Markdown supported.")
    """The Note content. Max length is 560 characters."""

    html_class = "note"
    postheader_template = "notes/_postheader_template.html"

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        """Returns the url for the note relative to the root."""
        return reverse('notes:detail', args=[self.id])

    def feed_item_content(self):
        """Returns the content for aggregated feed item indexes."""
        return self.content_html()

    def content_html(self):
        """Returns the content converted from markdown to HTML."""
        markdown = mistune.create_markdown(plugins=['url'])
        return markdown(self.content)

    def feed_item_header(self):
        """Returns the title for aggregated feed item indexes."""
        return False
        #return self.content_html() #timezone.localtime(self.published).strftime('%b. %d, %Y, %I:%M %p')

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