"""

"""

from django.db import models
from profiles.models import Profile
from feed.models import Tag, FeedItem
from syndications.models import TwitterSyndicatable, TwitterStatusUpdate, MastodonSyndicatable, MastodonStatusUpdate
from django.urls import reverse
from urllib.parse import urlparse

# An indieweb "Note" contenttype https://indieweb.org/note
class Note(MastodonSyndicatable, TwitterSyndicatable, FeedItem):
    """
    A Note model.

    Implements TwitterSyndicatable and FeedItem.
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
        return self.content

    def feed_item_header(self):
        """Returns the title for aggregated feed item indexes."""
        return self.published

    def to_twitter_status_update(self):
        """Converts the Note model to an object able to post to Twitter."""

        # Get the basic Twitter Status object from the content.
        update = TwitterStatusUpdate(status=self.content)

        # If Note is not replying to anything, return the update as it is.
        if self.in_reply_to is None:
            return update

        # Check if the reply to url is a twitter url, if it's a twitter status,
        # parse the screen name and status id from it.
        is_twitter_url, is_twitter_status, reply_to_screen_name, reply_to_status_id = TwitterSyndicatable.parse_twitter_url(self.in_reply_to)

        # If the reply to url is not a twitter url and is not a twitter status,
        # append the reply to url to the end of the Note content.
        if not is_twitter_url or not is_twitter_status:
            update.status = f'{self.content} {self.in_reply_to}'
            return update

        # If the Note content starts with the reply to screen name, then it's 
        # a reply.  Add that data to the update object.
        if self.content.lower().startswith(f'@{reply_to_screen_name.lower()}'):
            update.in_reply_to_status_id = reply_to_status_id
            return update

        # Otherwise, it's a quote tweet. Add that to the update object.
        update.attachment_url = self.in_reply_to
        return update

    def to_mastodon_status_update(self):
        """Converts the Note model to an object able to post to Mastodon."""

        # Get the basic Mastodon Status object from the content.
        status = MastodonStatusUpdate(self.content)

        # If Note is not replying to anything, return the status as it is.
        if self.in_reply_to is None:
            return status

        # Check the reply for a Mastodon Id.
        reply_to_id = MastodonSyndicatable.parse_mastodon_url(self.in_reply_to)

        # If no Mastodon Id, append the reply to url to the end of the 
        # Note content.
        if reply_to_id is None:
            status.status = f'{self.content} {self.in_reply_to}'
            return status

        
        # Add the reply_to_id and return
        status.reply_to_id = reply_to_id
        return status