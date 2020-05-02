from django.db import models
from profiles.models import Profile
from feed.models import Tag, FeedItem
from syndications.models import TwitterSyndicatable, TwitterStatusUpdate
from django.urls import reverse
from urllib.parse import urlparse

# Create your models here.
class Note(TwitterSyndicatable, FeedItem):
    content = models.CharField(max_length=560)

    def __str__(self):
        return self.content

    def get_absolute_url(self):
        return reverse('notes:detail', args=[self.id])

    def feed_item_content(self):
        return self.content

    def feed_item_header(self):
        return self.published

    def to_twitter_status_update(self):
        update = TwitterStatusUpdate(status=self.content)

        if self.in_reply_to is None:
            return update

        is_twitter_url, is_twitter_status, reply_to_screen_name, reply_to_status_id = TwitterSyndicatable.parse_twitter_url(self.in_reply_to)

        if not is_twitter_url or not is_twitter_status:
            update.status = f'{self.content} {self.in_reply_to}'
            return update

        if self.content.lower().startswith(f'@{reply_to_screen_name.lower()}'):
            update.in_reply_to_status_id = reply_to_status_id
            return update

        update.attachment_url = self.in_reply_to
        return update