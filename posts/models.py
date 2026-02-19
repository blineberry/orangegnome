from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from feed.fields import CommonmarkField
from feed.models import FeedItem

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

class Post(FeedItem):
    # h-entry properties
    summary_max = 280
    
    title_max = 100
   
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='posts', null=True, blank=True)

    # extra properties
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    
    postcontent_template = "posts/_post_summary.html"

    def __str__(self):
        return self.title_txt()

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.id, self.slug])

    def feed_item_content(self):
        return self.content_html()

    def feed_item_header(self):
        return self.title_txt()
    
    def to_mastodon_status(self):
        """Return the content that should be the Status of a mastodon post."""
        return f'{self.summary_txt()}\n\n{self.get_permalink()}'
    
    def get_mastodon_reply_to_url(self):
        """Return the url that should be checked for the in_reply_to_id."""
        return self.in_reply_to

    def get_mastodon_tags(self):
        """Return the tags that should be parsed and added to the status."""
        return self.tags.all() 
    
    def get_mastodon_idempotency_key(self):
        """Return a string to use as the Idempotency key for Status posts."""
        return str(self.id) + str(self.updated)
    
    def clean(self):
        super().clean()
        self.validate_publishable()

    def validate_publishable(self):
        super().validate_publishable()

        if not self.published:
            return
        
        if not self.summary_md or self.summary_md.isspace():
            raise ValidationError("Summary is required to publish.")
        

        if not self.content_md or self.content_md.isspace():
            raise ValidationError("Content is required to publish.")
        
        title_txt = self.title_txt()
        summary_txt = self.summary_txt()

        limits = (
            ("Title", len(title_txt), Post.title_max),
            ("Summary", len(summary_txt), Post.summary_max),
        )

        for limit in limits:
            if limit[1] > limit[2]:
                raise ValidationError("%s plain text count of %s must be less than the limit of %s to publish." % limit)