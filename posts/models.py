from django.db import models
from pages.models import Profile
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('posts:category', args=[self.id, self.slug])

class Tag(models.Model):
    title = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(max_length=50, db_index=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:tag', args=[self.id, self.slug])

class Post(models.Model):
    # h-entry properties
    name = models.CharField(max_length=100, unique=True)
    summary = models.CharField(max_length=120)
    content = models.TextField()
    published = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name='posts')
    
    # extra properties
    slug = models.SlugField(max_length=100, unique=True)
    tags = models.ManyToManyField(Tag, related_name='posts')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('posts:detail', args=[self.id, self.slug])