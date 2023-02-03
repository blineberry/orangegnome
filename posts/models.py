from django.db import models
from django.urls import reverse
from feed.models import FeedItem
from syndications.models import TwitterSyndicatable, TwitterStatusUpdate, MastodonSyndicatable, MastodonStatusUpdate
from feed.models import Tag
from profiles.models import Profile
import mistune

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('posts:category', args=[self.id, self.slug])

class Post(TwitterSyndicatable, MastodonSyndicatable, FeedItem):
    # h-entry properties
    summary = models.CharField(max_length=280, help_text="Markdown supported.")
    title = models.CharField(max_length=100, unique=True)
    content = models.TextField(help_text="HTML supported.")    
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='posts', null=True)

    # extra properties
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    
    postcontent_template = "posts/_post_summary.html"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.id, self.slug])

    def summary_html(self):
        markdown = mistune.create_markdown(plugins=['url'])
        return markdown(self.summary)

    def feed_item_content(self):
        return self.content

    def feed_item_header(self):
        return self.title

    def to_twitter_status(self):        
        """Return the content that should be the tweet status."""
        return f'{self.summary} {self.get_permalink()}'
    
    def get_twitter_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to
    
    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        return f'{self.summary}\n\n{self.get_permalink()}'
    
    def get_mastodon_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to

    def get_mastodon_tags(self):
        """Return the tags that should be parsed and added to the status."""
        return self.tags.all() 
    
    def get_mastodon_idempotency_key(self):
        """Return a string to use as the Idempotency key for Status posts."""
        return str(self.id) + str(self.updated)