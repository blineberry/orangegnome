"""
Implementation of the IndieWeb Bookmark post type.
https://indieweb.org/bookmark
"""

from django.db import models
from django.urls import reverse
from feed.models import FeedItem
from syndications.models import TwitterSyndicatable, MastodonSyndicatable
from django.template.loader import render_to_string

# Create your models here.
class Bookmark(MastodonSyndicatable, TwitterSyndicatable, FeedItem):
    """
    The Django model representing the bookmark.
    """

    url = models.CharField(max_length=2000)
    """
    The URL of the bookmark.
    """

    title = models.CharField(max_length=100, blank=True)
    """
    The title of the bookmark, probably the title of the URL page.
    """

    commentary = models.CharField(max_length=280, blank=True)
    """
    Content commenting on the content of the bookmark.
    """

    quote = models.CharField(max_length=280, blank=True)
    """
    Quote from the bookmarked content.
    """

    postheader_template = "bookmarks/_bookmark_postheader.html"
    postcontent_template = "bookmarks/_bookmark_postcontent.html"

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        """Returns the url for the bookmark relative to the root."""
        return reverse('bookmarks:detail', args=[self.id])

    @staticmethod
    def is_none_or_whitespace(str):
        """
        Returns True if string is neither None nor an empty string, nor a 
        string only made of whitespace.
        """
        if str is None:
            return False

        if str == "":
            return False

        if str.isspace():
            return False

        return True

    def has_quote(self):
        """Returns True if Bookmark has a quote."""
        return Bookmark.is_none_or_whitespace(self.quote)

    def has_commentary(self):
        """Returns True if Bookmark has commentary."""
        return Bookmark.is_none_or_whitespace(self.commentary)

    def has_content(self):
        """Returns True if Bookmark has either quote or commentary."""
        # True if we have commentary
        if self.has_commentary():
            return True

        # True if we have a quote
        return self.has_quote()
    
    def has_quote_and_commentary(self):
        """Returns True if Bookmark has both quote and commentary."""
        return self.has_quote() and self.has_commentary()

    def get_title_or_url(self):
        """
        Returns the bookmark title if it exists, otherwise returns the url.
        """
        if self.title is not None and self.title.isspace() == False and self.title != "":
            return self.title

        return self.url    
    
    def feed_item_header(self):
        """
        Returns the title for feed item indexes.
        """
        return self.get_title_or_url()

    def feed_item_content(self):
        """Returns the content for aggregated feed item indexes."""
        return render_to_string('bookmarks/_bookmark_postcontent.html', { 'item': self })

    def feed_item_link(self):
        return self.url

    def to_twitter_status(self):
        """Return the content that should be the tweet status."""

        if self.has_content() is not True:
            raise Exception("No content to tweet.")

        content = ""
        quote_content = "“" + self.quote + "”\n\n"
        commentary_content = self.commentary + "\n\n"

        # If the Bookmark has a quote and it's length (plus 2 characters for 
        # newlines plus the length of a link) is not longer than what's allowed
        # put the quote in 
        if self.has_quote() and (len(quote_content) + TwitterSyndicatable.tweet_link_length) < TwitterSyndicatable.tweet_length_limit:
            content = quote_content

        if self.has_commentary() and (len(content) + len(commentary_content) + TwitterSyndicatable.tweet_link_length) < TwitterSyndicatable.tweet_length_limit:
            content = content + commentary_content

        return content + self.url

    def get_twitter_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to      

    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        if self.has_content() is not True:
            raise Exception("No content to post to Mastodon.")

        content = ""
        
        if self.has_quote():
            content = "“" + self.quote + "”\n\n"
        
        if self.has_commentary():
            content = content + self.commentary + "\n\n"

        return content + self.url
    
    def get_mastodon_idempotency_key(self):
        """Return a string to use as the Idempotency key for Status posts."""
        return str(self.id) + str(self.updated)
    
    def get_mastodon_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to

    def get_mastodon_tags(self):
        """Return the tags that should be parsed and added to the status."""
        return self.tags.all()