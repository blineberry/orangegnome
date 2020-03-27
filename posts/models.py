from django.db import models
from profiles.models import Profile
from django.urls import reverse
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

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('posts:tag', args=[self.id, self.slug])

def get_default_author():
    return Profile.objects.get()[0]

class Post(FeedItem):
    # h-entry properties
    title = models.CharField(max_length=100, unique=True)
    summary = models.CharField(max_length=120)
    content = models.TextField()
    published = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='posts', null=True)
    
    # extra properties
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    tags = models.ManyToManyField(Tag, related_name='posts')
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.id, self.slug])