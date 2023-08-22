from django.db import models
from feed.models import FeedItem
from syndications.models import MastodonSyndicatable
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator

# Create your models here.
class Repost(MastodonSyndicatable, FeedItem):
    url = models.URLField(null=True,blank=True)
    source_name=models.CharField(null=True,blank=True,max_length=1000)
    content = models.TextField()
    source_author_name = models.CharField(max_length=200, default="Anonymous")
    source_author_url = models.URLField(null=True,blank=True)

    postheader_template = "reposts/_repost_postheader.html"
    postcontent_template = "reposts/_repost_postcontent.html"
    published_verb = "Reposted"

    def __str__(self):
        t = Truncator(strip_tags(self.content))
        return t.chars(50)

    def get_absolute_url(self):
        """Returns the url for the bookmark relative to the root."""
        return reverse('reposts:detail', args=[self.id])
        
    def is_mastodon_boost(self):
        return True
    
    def get_mastodon_url(self):
        return self.url
    
    def to_text(self):
        return "Reposted " + self.source_author_name