from django.db import models
from profiles.models import Profile
from feed.models import FeedItem, Tag
from syndications.models import TwitterSyndicatable
from django.urls import reverse

# Create your models here.
class Publishable(models.Model):
    is_published = models.BooleanField(default=False)

    class Meta:
        abstract = True

class NoteBase(Publishable):    
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    published = models.DateTimeField(null=True)
    short_content = models.CharField(max_length=280)
    tags = models.ManyToManyField(Tag, related_name='notes')

    class Meta:
        abstract = True

class Note(NoteBase, FeedItem, TwitterSyndicatable):
    def __str__(self):
        return self.short_content

    def get_absolute_url(self):
        return reverse('notes:detail', args=[self.id])

    def feed_item_content(self):
        return self.short_content

    def feed_item_header(self):
        return self.published

    def to_twitter_status(self):
        return self.short_content