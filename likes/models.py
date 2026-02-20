from django.db import models
from feed.models import FeedItem
from django.urls import reverse
from django.core.exceptions import ValidationError

# Create your models here.
class Like(FeedItem):

    postheader_template = "likes/_like_postheader.html"
    postcontent_template = "likes/_like_postcontent.html"

    published_verb = "Liked"

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        """Returns the url for the bookmark relative to the root."""
        return reverse('likes:detail', args=[self.id])
    
    def to_text(self):
        return self.author.name + " liked " + self.url
    
    def is_mastodon_favorite(self):
        return True
    
    def get_mastodon_url(self):
        return self.url
    

    def clean(self):
        super().clean()
        self.validate_publishable()
    
    def validate_publishable(self):
        if self.url is None:
            raise ValidationError("Url is required.")