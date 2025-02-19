"""
Implementation of the IndieWeb Bookmark post type.
https://indieweb.org/bookmark
"""

from django.db import models
from django.urls import reverse
from feed.models import FeedItem
from syndications.models import TwitterSyndicatable, MastodonSyndicatable
from django.template.loader import render_to_string
from feed.fields import CommonmarkField, CommonmarkInlineField
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
class Bookmark(MastodonSyndicatable, TwitterSyndicatable, FeedItem):
    """
    The Django model representing the bookmark.
    """

    url = models.URLField(max_length=2048)
    """
    The URL of the bookmark.
    """

    title_txt = models.TextField(blank=True)
    title_max = 100
    title_md = CommonmarkInlineField(blank=True, txt_field='title_txt', html_field='title_html', verbose_name="title", help_text="CommonMark supported. Inline elements only.")
    title_html = models.TextField(blank=True)
    """
    The title of the bookmark, probably the title of the URL page.
    """
    commentary_txt = models.TextField(blank=True)
    commentary_html = models.TextField(blank=True)
    commentary_max = 280
    commentary_md = CommonmarkField(blank=True, txt_field='commentary_txt', html_field='commentary_html', verbose_name="commentary", help_text="CommonMark supported.")
    """
    Content commenting on the content of the bookmark.
    """

    quote_txt = models.TextField(blank=True)
    quote_html = models.TextField(blank=True)
    quote_max = 280
    quote_md = CommonmarkField(blank=True, txt_field='quote_txt', html_field='quote_html', verbose_name="quote", help_text="CommonMark supported.")
    """
    Quote from the bookmarked content.
    """

    commonmark_rendered_at = models.DateTimeField(null=True)

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
        return Bookmark.is_none_or_whitespace(self.quote_md)

    def has_commentary(self):
        """Returns True if Bookmark has commentary."""
        return Bookmark.is_none_or_whitespace(self.commentary_md)

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

    def get_title_or_url_html(self):
        """
        Returns the bookmark title if it exists, otherwise returns the url.
        """
        if self.title_html is not None and self.title_html.isspace() == False and self.title_html != "":
            return self.title_html

        return self.url    

    def get_title_or_url_txt(self):
        """
        Returns the bookmark title if it exists, otherwise returns the url.
        """
        if self.title_txt is not None and self.title_txt.isspace() == False and self.title_txt != "":
            return self.title_txt

        return self.url  
    
    def feed_item_header(self):
        """
        Returns the title for feed item indexes.
        """
        return self.get_title_or_url_txt()

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
            content = "“" + self.quote_txt + "”\n\n"
        
        if self.has_commentary():
            content = content + self.commentary_txt + "\n\n"

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
    
    def render_title(self):
        self.title_txt = CommonmarkInlineField.md_to_txt(self.title_md)
        self.title_html = CommonmarkInlineField.md_to_html(self.title_md)
    
    def render_quote(self):
        self.quote_txt = CommonmarkField.md_to_txt(self.quote_md)
        self.quote_html = CommonmarkField.md_to_html(self.quote_md)
    
    def render_commentary(self):
        self.commentary_txt = CommonmarkField.md_to_txt(self.commentary_md)
        self.commentary_html = CommonmarkField.md_to_html(self.commentary_md)
    
    def render_commonmark_fields(self):
        self.render_title()
        self.render_quote()
        self.render_commentary()
        self.commonmark_rendered_at = timezone.now()
    
    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        return result
    
    # def clean(self, *args, **kwargs):
    #     return super().clean()
    #     self.render_commonmark_fields()

    #     self.validate_publishable()
    #     return super().clean()
    
    def is_publishable(self):
        title_txt = self.title_txt
        quote_txt = self.quote_txt
        commentary_txt = self.commentary_txt

        limits = (
            ("Title", len(title_txt), Bookmark.title_max),
            ("Quote", len(quote_txt), Bookmark.quote_max),
            ("Commentary", len(commentary_txt), Bookmark.commentary_max),
        )

        for limit in limits:
            if limit[1] > limit[2]:
                return False
            
        return True
    
    # def validate_publishable(self):
    #     return
    #     if not self.published:
    #         return
        
    #     title_txt = self.title_txt
    #     quote_txt = self.quote_txt
    #     commentary_txt = self.commentary_txt

    #     limits = (
    #         ("Title", len(title_txt), Bookmark.title_max),
    #         ("Quote", len(quote_txt), Bookmark.quote_max),
    #         ("Commentary", len(commentary_txt), Bookmark.commentary_max),
    #     )

    #     for limit in limits:
    #         if limit[1] > limit[2]:
    #             raise ValidationError("%s plain text count of %s must be less than the limit of %s to publish." % limit)
    