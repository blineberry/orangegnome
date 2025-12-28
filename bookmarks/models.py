"""
Implementation of the IndieWeb Bookmark post type.
https://indieweb.org/bookmark
"""

from django.db import models
from django.urls import reverse
from feed.models import FeedItem
from django.template.loader import render_to_string
from feed.fields import CommonmarkField, CommonmarkInlineField
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
class Bookmark(FeedItem):
    """
    The Django model representing the bookmark.
    """

    url = models.URLField(max_length=2048)
    """
    The URL of the bookmark.
    """

    title_md = models.TextField(blank=True, verbose_name="title", help_text="Markdown supported. Inline elements only.")
    """
    The title of the bookmark, probably the title of the URL page.
    """

    title_max = 100

    def title_txt(self):
        return CommonmarkInlineField.md_to_txt(self.title_md)
    
    def title_html(self):
        return CommonmarkInlineField.md_to_html(self.title_md)

    
    commentary_md = models.TextField(blank=True, verbose_name="commentary", help_text="Markdown supported.")
    """
    Content commenting on the content of the bookmark.
    """

    commentary_max = 280    
    
    def commentary_txt(self):
        return CommonmarkField.md_to_txt(self.commentary_md)
    
    def commentary_html(self):
        return CommonmarkField.md_to_html(self.commentary_md)

    quote_md = models.TextField(blank=True, verbose_name="quote", help_text="CommonMark supported.")
    """
    Quote from the bookmarked content.
    """

    quote_max = 280

    def quote_txt(self):
        return CommonmarkField.md_to_txt(self.quote_md)
    
    def quote_html(self):
        return CommonmarkField.md_to_html(self.quote_md)

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
        html = self.title_html()
        if html is None or html.isspace() or html == "":
            return self.url

        return html

    def get_title_or_url_txt(self):
        """
        Returns the bookmark title if it exists, otherwise returns the url.
        """
        txt = self.title_txt()

        if txt is None or txt.isspace() or txt == "":
            return self.url  
        
        return txt        
    
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

    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        if self.has_content() is not True:
            raise Exception("No content to post to Mastodon.")

        content = ""
        
        if self.has_quote():
            content = "“" + self.quote_txt() + "”\n\n"
        
        if self.has_commentary():
            content = content + self.commentary_txt() + "\n\n"

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
        raise NotImplementedError()
        return
        self.title_txt = CommonmarkInlineField.md_to_txt(self.title_md)
        self.title_html = CommonmarkInlineField.md_to_html(self.title_md)
    
    def render_quote(self):
        raise NotImplementedError()
        self.quote_txt = CommonmarkField.md_to_txt(self.quote_md)
        self.quote_html = CommonmarkField.md_to_html(self.quote_md)
    
    def render_commentary(self):
        raise NotImplementedError()
        self.commentary_txt = CommonmarkField.md_to_txt(self.commentary_md)
        self.commentary_html = CommonmarkField.md_to_html(self.commentary_md)
    
    def render_commonmark_fields(self):
        raise NotImplementedError()
        self.render_title()
        self.render_quote()
        self.render_commentary()
        self.commonmark_rendered_at = timezone.now()
    
    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        return result
    
    def clean(self):
        super().clean()
        self.validate_publishable()
    
    def is_publishable(self):
        title_txt = self.title_txt()
        quote_txt = self.quote_txt()
        commentary_txt = self.commentary_txt()

        limits = (
            ("Title", len(title_txt), Bookmark.title_max),
            ("Quote", len(quote_txt), Bookmark.quote_max),
            ("Commentary", len(commentary_txt), Bookmark.commentary_max),
        )

        for limit in limits:
            if limit[1] > limit[2]:
                return False
            
        return True
    
    def validate_publishable(self):
        if not self.published:
            return
        
        title_txt = self.title_txt()
        quote_txt = self.quote_txt()
        commentary_txt = self.commentary_txt()

        limits = (
            ("Title", len(title_txt), Bookmark.title_max),
            ("Quote", len(quote_txt), Bookmark.quote_max),
            ("Commentary", len(commentary_txt), Bookmark.commentary_max),
        )

        for limit in limits:
            if limit[1] > limit[2]:
                raise ValidationError("%s plain text count of %s must be less than the limit of %s to publish." % limit)
    