from django.db import models
from django.urls import reverse
from feed.models import FeedItem
from syndications.models import TwitterSyndicatable, TwitterStatusUpdate, MastodonSyndicatable, MastodonStatusUpdate
from feed.models import Tag
from profiles.models import Profile

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
    summary = models.CharField(max_length=280)
    title = models.CharField(max_length=100, unique=True)
    content = models.TextField()    
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='posts', null=True)

    # extra properties
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.id, self.slug])

    def feed_item_content(self):
        return self.content

    def feed_item_header(self):
        return self.title

    def to_twitter_status_update(self):
        update = TwitterStatusUpdate(status=f'{self.summary} {self.get_permalink()}')
        
        if self.in_reply_to is None:
            return update

        is_twitter_url, is_twitter_status, reply_to_screen_name, reply_to_status_id = TwitterSyndicatable.parse_twitter_url(self.in_reply_to)

        if not is_twitter_url or not is_twitter_status:
            return update

        if self.summary.lower().startswith(f'@{reply_to_screen_name.lower()}'):
            update.in_reply_to_status_id = reply_to_status_id
            return update

        update.attachment_url = self.in_reply_to
        return update    

    def to_mastodon_status_update(self):
        """Converts the Post model to an object able to post to Mastodon."""

        # Get the basic Mastodon Status object from the content.
        status = MastodonStatusUpdate(status=f'{self.summary} {self.get_permalink()}')

        # If Note is not replying to anything, return the status as it is.
        if self.in_reply_to is None:
            return status

        # Check the reply to url for a mastodon-looking id.
        in_reply_to_id = MastodonSyndicatable.parse_mastodon_url(self.in_reply_to)

        # If no Mastodon Id in the reply to url, return the status.
        if in_reply_to_id is None:
            status.status = f'{self.content} {self.in_reply_to}'
            return status

        # Add the reply_to_id and return
        status.in_reply_to_id = in_reply_to_id
        return status