from django.db import models
from django.urls import reverse
from feed.models import FeedItemBase, FeedItem
from syndications.models import TwitterSyndicatable
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

class Post(FeedItemBase, TwitterSyndicatable, FeedItem):
    # h-entry properties
    short_content = models.CharField(max_length=280)
    title = models.CharField(max_length=100, unique=True)
    long_content = models.TextField()    
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='posts', null=True)

    # extra properties
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        print(reverse('posts:detail', args=[self.id, self.slug]))
        return reverse('posts:detail', args=[self.id, self.slug])

    def feed_item_content(self):
        return self.long_content

    def feed_item_header(self):
        return self.title

    def to_twitter_status(self):
        return f'{self.short_content} {self.get_absolute_url()}'