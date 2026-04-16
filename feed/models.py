from django.db import models
from django.urls import reverse
from profiles.models import Profile
from django.conf import settings
from django.utils import timezone
from webmentions.models import Webmentionable
from syndications.models import MastodonSyndicatable
from django.core.exceptions import ValidationError
from syndications.models import MastodonStatus, Syndication as SyndicationsSyndication
from .fields import CommonmarkField
from django.contrib.contenttypes.fields import (GenericForeignKey,
                                                GenericRelation)
from django_resized import ResizedImageField
from django_resized.forms import ResizedImageFieldFile
from uuid import uuid4
from datetime import date
from .storage import PublicAzureStorage
from django.utils.html import mark_safe, strip_tags
from django.template.loader import render_to_string
from django.utils.text import Truncator

def convert_commonmark_to_plain_text(input:str, strip:bool=True):
    return CommonmarkField.md_to_txt(input, strip)

def convert_commonmark_to_html(input:str, block_content:bool=True):
    return CommonmarkField.md_to_html(input, block_content)

# Custom upload_to callable
# Heavily influenced from https://stackoverflow.com/a/15141228/814492
def upload_to_callable(instance, filename):
    ext = filename.split('.')[-1]

    filename = '{}.{}'.format(uuid4().hex, ext)

    d = date.today()

    return '{0}/{1}'.format(d.strftime('%Y/%m/%d'),filename)

class OGResizedImageFieldFile(ResizedImageFieldFile):
    def save(self, name, content, save=True):
        super().save(name, content, save)
        self.field.update_dimension_fields(self.instance, force=True)

class OGResizedImageField(ResizedImageField):
    attr_class = OGResizedImageFieldFile

# Create your models here.
class Image(models.Model):
    image = OGResizedImageField(
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

    description = models.CharField(blank=True, max_length=255)

    def __str__(self):
        return self.description
    
    def image_tag(self):
        """Returns html for the Admin change view to display the uploaded image."""
        if self.image is None:
            return ""

        return mark_safe('<img src="%s" style="max-width: 200px; max-height: 200px; width: auto; height: auto;" />' % (self.image.url))

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('feed:tag', args=[self.id, self.slug])

    def test(self):
        return self.name

    def to_pascale_case(self, strip_special_characters = True):
        name = self.name

        if strip_special_characters:
            name = ''.join(filter(lambda character : character.isalnum() or character == ' ',self.name))

        return "".join(name.title().split())

    def to_hashtag(self, strip_special_characters = True):
        return "#" + self.to_pascale_case(strip_special_characters)

class FeedItem(Webmentionable, MastodonSyndicatable):
    class PostType(models.TextChoices):
        ARTICLE = 'ARTICLE'
        BOOKMARK = 'BOOKMARK'
        LIKE = 'LIKE'
        NOTE = 'NOTE'
        PHOTO = 'PHOTO'
        REPOST = 'REPOST'

    post_type = models.CharField(choices=PostType, null=True, blank=True, max_length=8)
    created = models.DateTimeField(null=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True)
    published = models.DateTimeField(null=True,blank=True)
    tags = models.ManyToManyField(Tag, related_name='feed_items',blank=True)
    in_reply_to = models.CharField(max_length=2000, blank=True, null=True)
    source_name=models.CharField(null=True,blank=True,max_length=1000)
    source_author_name = models.CharField(max_length=200, default="Anonymous")
    source_author_url = models.URLField(null=True,blank=True)

    images = models.ManyToManyField(Image, through="PostImage", related_name="posts")

    content_md = models.TextField(help_text="Markdown supported.", blank=True, null=True)
    def content_txt(self):
        """Returns the content converted from markdown to HTML."""
        return convert_commonmark_to_plain_text(self.content_md)
    
    def content_html(self):
        """Returns the content converted from markdown to HTML."""
        return convert_commonmark_to_html(self.content_md)
    
    summary_md = models.TextField(help_text="Markdown supported.", blank=True, null=True)

    def summary_txt(self):
        return convert_commonmark_to_plain_text(self.summary_md)

    def summary_html(self):
        return convert_commonmark_to_html(self.summary_md)
    
    quote_md = models.TextField(blank=True, verbose_name="quote", help_text="CommonMark supported.")

    def quote_txt(self):
        return convert_commonmark_to_plain_text(self.quote_md)
    
    def quote_html(self):
        return convert_commonmark_to_html(self.quote_md)
    
    title_md = models.TextField(blank=True, verbose_name="title", help_text="Markdown supported. Inline elements only.")

    def title_txt(self):
        return convert_commonmark_to_plain_text(self.title_md)
    
    def title_html(self):
        return convert_commonmark_to_html(self.title_md, False)
    
    url = models.URLField(max_length=2048,null=True,blank=True)

    slug = models.SlugField(max_length=100, null=True)

    @staticmethod
    def get_title_max(post_type):
        # Bookmark and Article
        return 100
    
    @staticmethod
    def get_quote_max(post_type):
        # Bookmark
        return 280  
    
    @staticmethod
    def get_content_max(post_type):
        if post_type == FeedItem.PostType.BOOKMARK:
            return 280
        
        if (post_type == FeedItem.PostType.NOTE or
            post_type == FeedItem.PostType.PHOTO):
            return 560
        
        return

    @staticmethod
    def get_summary_max(post_type):
        # Article
        return 280
    
    @staticmethod
    def get_html_class(post_type):
        if post_type == FeedItem.PostType.BOOKMARK:
            return 'bookmark'
        
        if post_type == FeedItem.PostType.LIKE:
            return 'like'
        
        if post_type == FeedItem.PostType.NOTE:
            return 'note'
        
        if post_type == FeedItem.PostType.PHOTO:
            return 'photo'
        
        return
    
    @staticmethod
    def get_published_verb(post_type):
        if post_type == FeedItem.PostType.BOOKMARK:
            return 'Bookmarked'
        
        if post_type == FeedItem.PostType.LIKE:
            return 'Liked'
        
        if post_type == FeedItem.PostType.NOTE:
            return 'Noted'
        
        if post_type == FeedItem.PostType.REPOST:
            return 'Reposted'
        
        return 'Posted'

    @staticmethod
    def get_postheader_template(post_type):
        if post_type == FeedItem.PostType.BOOKMARK:
            return 'bookmarks/_bookmark_postheader.html'
        
        if post_type == FeedItem.PostType.LIKE:
            return 'likes/_like_postheader.html'
        
        if post_type == FeedItem.PostType.NOTE:
            return 'notes/_postheader_template.html'
        
        if post_type == FeedItem.PostType.PHOTO:
            return 'photos/_postheader_template.html'

        if post_type == FeedItem.PostType.REPOST:
            return 'reposts/_repost_postheader.html'
        
        return 'feed/_postheader_template.html'
    
    @staticmethod
    def get_postcontent_template(post_type):
        if post_type == FeedItem.PostType.BOOKMARK:
            return 'bookmarks/_bookmark_postcontent.html'
        
        if post_type == FeedItem.PostType.LIKE:
            return 'likes/_like_postcontent.html'
        
        if post_type == FeedItem.PostType.ARTICLE:
            return 'posts/_post_summary.html'
        
        if post_type == FeedItem.PostType.REPOST:
            return 'reposts/_repost_postcontent.html'

        return 'feed/_postbody_template.html'

    def title_max(self):
        return FeedItem.get_title_max(self.post_type)

    def quote_max(self):
        return FeedItem.get_quote_max(self.post_type)     
        
    def content_max(self):
        return FeedItem.get_content_max(self.post_type)
    
    def summary_max(self):
        return FeedItem.get_summary_max(self.post_type)
    
    def html_class(self):
        return FeedItem.get_html_class(self.post_type)
    
    def postheader_template(self):
        return FeedItem.get_postheader_template(self.post_type)
    
    def postcontent_template(self):
        return FeedItem.get_postcontent_template(self.post_type)

    @staticmethod
    def get_site_url():
        return settings.SITE_URL
    
    def is_published(self):
        if self.published is None:
            return False
        
        if self.published > timezone.now():
            return False
        
        return True
    
    def get_absolute_url(self):
        """Returns the url for the post relative to the root."""
        if self.post_type == FeedItem.PostType.ARTICLE:
            return reverse('feed:detail', args=[self.id, self.slug])
            
        return reverse('feed:detail', args=[self.id])

    def get_permalink(self):
        return self.get_site_url() + self.get_absolute_url()

    def __str__(self):
        if (self.post_type == FeedItem.PostType.BOOKMARK or 
            self.post_type == FeedItem.PostType.LIKE):
            return self.url
        
        if (self.post_type == FeedItem.PostType.NOTE or
            self.post_type == FeedItem.PostType.NOTE):
            return self.content_txt()
        
        if self.post_type == FeedItem.PostType.ARTICLE:
            return self.title_txt()
        
        if self.post_type == FeedItem.PostType.REPOST:
            t = Truncator(strip_tags(self.content_txt()))
            return t.chars(50)
        
        return 'FeedItem'

    def is_post(self):
        return hasattr(self, 'post')

    def is_note(self):
        return hasattr(self, 'note')

    def is_photo(self):
        return hasattr(self, 'photo')

    def is_exercise(self):
        return hasattr(self, 'exercise')

    def is_bookmark(self):
        return hasattr(self, 'bookmark')

    def is_like(self):
        return hasattr(self, 'like')

    def is_repost(self):
        return hasattr(self, 'repost')

    def get_child(self):
        if self.is_post():
            return self.post
        
        if self.is_note():
            return self.note

        if self.is_photo():
            return self.photo

        if self.is_exercise():
            return self.exercise
        
        if self.is_bookmark():
            return self.bookmark
        
        if self.is_like():
            return self.like
        
        if self.is_repost():
            return self.repost

        raise NotImplementedError
    
    def get_type_name(self):
        return self._meta.verbose_name
        
    def get_type_name_plural(self):
        return self._meta.verbose_name_plural
    
    def get_type_verb(self):
        return self._meta.object_verb

    def meta_template(self):
        return f'{ self._meta.app_label }/_meta.html'

    def feed_item_template(self):
        return None

    def feed_item_header(self):
        """
        Returns the title for feed item indexes.
        """
        if self.post_type == FeedItem.PostType.BOOKMARK:
            return self.get_title_or_url_txt()
        
        if (self.post_type == FeedItem.PostType.NOTE or
            self.post_type == FeedItem.PostType.PHOTO):
            return self.content_txt()
        
        if self.post_type == FeedItem.PostType.ARTICLE:
            return self.title_txt()
        
        if self.post_type == FeedItem.PostType.REPOST:
            return f'Reposted {self.source_author_name}'
        
        return None
    
    def feed_item_content(self):
        """Returns the content for aggregated feed item indexes."""
        if self.post_type == FeedItem.PostType.BOOKMARK:
            return render_to_string('feed/bookmark_content.html', { 'bookmark': self })
        
        if (self.post_type == FeedItem.PostType.NOTE or
            self.post_type == FeedItem.PostType.ARTICLE):
            return self.content_html()
        
        if self.post_type == FeedItem.PostType.PHOTO:
            return render_to_string('photos/_photo_content.html', { 'photo': self })
        
        if self.post_type == FeedItem.PostType.REPOST:
            return render_to_string('reposts/_repost_content.html', { 'item': self })
        
        return None
    
    def feed_item_link(self):
        if self.post_type == FeedItem.PostType.BOOKMARK:
            return self.url
        return self.get_child().get_permalink()
    
    def to_text(self):
        if self.post_type == FeedItem.PostType.REPOST:
            return "Reposted " + self.source_author_name
        
        return ""
    
    def get_edit_link(self):
        model_name = self._meta.model_name

        if self.post_type == FeedItem.PostType.ARTICLE:
            model_name = 'article'

        if self.post_type == FeedItem.PostType.BOOKMARK:
            model_name = 'bookmark'
        
        if self.post_type == FeedItem.PostType.LIKE:
            model_name = 'like'

        if self.post_type == FeedItem.PostType.NOTE:
            model_name = 'note'
        
        if self.post_type == FeedItem.PostType.PHOTO:
            model_name = 'photo'
            
        if self.post_type == FeedItem.PostType.REPOST:
            model_name = 'repost'        
        
        return reverse(f"admin:{self._meta.app_label}_{model_name}_change", args=(self.pk,))

    def should_send_webmentions(self):
        if self.published:
            return True
        
        return False
    
    def clean(self):
        super().clean()
        self.validate_publishable()

    def validate_publishable(self):
        """
        Some fields are only required to publish, not to save as drafts. This 
        method validates those fields.
        """

        # If the model is not `published`, then the object passes.
        if not self.published:
            return
        
        # Every feed item needs an author to publish.
        if not self.author:
            raise ValidationError("Published posts must have an author.")
        
        if self.post_type == FeedItem.PostType.BOOKMARK:
            if self.url is None:
                raise ValidationError("Url is required.")
            
            title_txt = self.title_txt()
            quote_txt = self.quote_txt()
            content_txt = self.content_txt()

            limits = (
                ("Title", len(title_txt), self.title_max()),
                ("Quote", len(quote_txt), self.quote_max()),
                ("Content", len(content_txt), self.content_max()),
            )

            for limit in limits:
                if limit[1] > limit[2]:
                    raise ValidationError("%s plain text count of %s must be less than the limit of %s to publish." % limit)
        
        if self.post_type == FeedItem.PostType.LIKE:
            if self.url is None:
                raise ValidationError("Url is required.")
            
        if (self.post_type == FeedItem.PostType.NOTE or
            self.post_type == FeedItem.PostType.PHOTO):
            content_txt = self.content_txt()

            if len(content_txt) > self.content_max():
                raise ValidationError("Plain text count of %s must be less than the limit of %s to publish." % (len(content_txt), self.content_max()))
            
        if self.post_type == FeedItem.PostType.ARTICLE:
            if not self.summary_md or self.summary_md.isspace():
                raise ValidationError("Summary is required to publish.")
            
            if not self.content_md or self.content_md.isspace():
                raise ValidationError("Content is required to publish.")
            
            title_txt = self.title_txt()
            summary_txt = self.summary_txt()

            limits = (
                ("Title", len(title_txt), self.title_max()),
                ("Summary", len(summary_txt), self.summary_max()),
            )

            for limit in limits:
                if limit[1] > limit[2]:
                    raise ValidationError("%s plain text count of %s must be less than the limit of %s to publish." % limit)

        
    def commonmark_to_html(self, commonmark:str, block_content:bool=True):
        return convert_commonmark_to_html(commonmark, block_content)
    
    def commonmark_to_plain(self, commonmark:str, strip:bool=True):
        return convert_commonmark_to_plain_text(commonmark, strip)
    

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
        return FeedItem.is_none_or_whitespace(self.quote_md)

    def has_content(self):
        """Returns True if Bookmark has content."""
        return FeedItem.is_none_or_whitespace(self.content_md)

    def has_quote_or_content(self):
        """Returns True if post has either quote or content."""
        # True if we have content
        if self.has_content():
            return True

        # True if we have a quote
        return self.has_quote()
    
    def has_quote_and_content(self):
        """Returns True if post has both quote and content."""
        return self.has_quote() and self.has_content()

    def get_title_or_url_html(self):
        """
        Returns the title if it exists, otherwise returns the url.
        """
        html = self.title_html()
        if html is None or html.isspace() or html == "":
            return self.url

        return html

    def get_title_or_url_txt(self):
        """
        Returns the title if it exists, otherwise returns the url.
        """
        txt = self.title_txt()

        if txt is None or txt.isspace() or txt == "":
            return self.url  
        
        return txt

    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        if self.post_type == FeedItem.PostType.BOOKMARK:
            if self.has_quote_or_content() is not True:
                raise Exception("No content to post to Mastodon.")

            content = ""
        
            if self.has_quote():
                content = "“" + self.quote_txt() + "”\n\n"
        
            if self.has_content():
                content = content + self.content_txt() + "\n\n"

            return content + self.url
        
        if (self.post_type == FeedItem.PostType.NOTE or
            self.post_type == FeedItem.PostType.PHOTO):
            return self.content_txt()
        
        if self.post_type == FeedItem.PostType.ARTICLE:
            return f'{self.summary_txt()}\n\n{self.get_permalink()}'
        
        raise Exception("No content to post to Mastodon.")
    
    def get_mastodon_idempotency_key(self):
        """Return a string to use as the Idempotency key for Status posts."""
        return str(self.id) + str(self.updated)
    
    def get_mastodon_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to

    def get_mastodon_tags(self):
        """Return the tags that should be parsed and added to the status."""
        return self.tags.all()
    
    def is_mastodon_favorite(self):
        if self.post_type == FeedItem.PostType.LIKE:
            return True
        
        return False
    
    def is_mastodon_boost(self):
        if self.post_type == FeedItem.PostType.REPOST:
            return True
        
        return False
    
    def get_mastodon_url(self):
        if (self.post_type == FeedItem.PostType.LIKE or
            self.post_type == FeedItem.PostType.REPOST):
            return self.url
        
        return None
    
    def has_mastodon_media(self):
        """Returns True if the Model has media to upload."""
        return self.image() is not None
    
    def get_mastodon_media_image_field(self):
        """Returns the ImageField for the media."""
        return self.image()
    
    def get_mastodon_media_description(self):
        """Returns the description for the media."""
        return self.alternative_text
    
    def image(self):
        image = self.images.first()

        if image is None:
            return None
        
        return image.image
    
    def image_height(self):        
        image = self.images.first()

        if image is None:
            return 0
        
        return image.image_height
    
    def image_width(self):
        image = self.images.first()

        if image is None:
            return 0
        
        return image.image_width
    
    def alternative_text(self):
        image = self.images.first()

        return self.postimage_set.get(image = image).alt

    # From https://stackoverflow.com/a/37965068/814492
    def image_tag(self):
        """Returns html for the Admin change view to display the uploaded image."""
        if self.image() is None:
            return ""

        return mark_safe('<img src="%s" style="max-width: 200px; max-height: 200px; width: auto; height: auto;" />' % (self.image().url))

    image_tag.short_description = 'Preview'
        
class Syndication(SyndicationsSyndication):
    syndicated_post = models.ForeignKey(FeedItem, on_delete=models.CASCADE, related_name="syndications")

class PostImage(models.Model):
    image = models.ForeignKey(Image,on_delete=models.CASCADE)
    post = models.ForeignKey(FeedItem, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(blank=True, null=True, default=50)
    alt = models.CharField(blank=True, max_length=255)
    feature = models.BooleanField(default=False)

    def __str__(self):
        return self.image.description

    def image_tag(self):
        """Returns html for the Admin change view to display the uploaded image."""
        if self.image is None or self.image.image is None:
            return ""

        return mark_safe('<img src="%s" style="max-width: 200px; max-height: 200px; width: auto; height: auto;" />' % (self.image.image.url))

    class Meta:
        ordering = ["order"]

class PostTypeManager(models.Manager):
    def __init__(self, post_type):
        super().__init__()
        self.post_type=post_type
    
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(post_type=self.post_type)        

class Bookmark(FeedItem):
    objects = PostTypeManager(FeedItem.PostType.BOOKMARK)

    class Meta:
        proxy = True

class Like(FeedItem):
    objects = PostTypeManager(FeedItem.PostType.LIKE)

    class Meta:
        proxy = True

class Note(FeedItem):
    objects = PostTypeManager(FeedItem.PostType.NOTE)

    class Meta:
        proxy = True

class Photo(FeedItem):
    objects = PostTypeManager(FeedItem.PostType.PHOTO)

    class Meta:
        proxy = True

class Article(FeedItem):
    objects = PostTypeManager(FeedItem.PostType.ARTICLE)

    class Meta:
        proxy = True

class Repost(FeedItem):
    objects = PostTypeManager(FeedItem.PostType.REPOST)

    class Meta:
        proxy = True