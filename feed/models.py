from django.db import models
from django.urls import reverse
from profiles.models import Profile
from django.conf import settings

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('feed:tag', args=[self.id, self.slug])

    def test(self):
        return self.name

class FeedItem(models.Model):
    is_published = models.BooleanField(default=False)
    updated = models.DateTimeField(null=True)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True)
    published = models.DateTimeField(null=True)
    tags = models.ManyToManyField(Tag, related_name='feed_items',blank=True)

    @staticmethod
    def get_site_url():
        return settings.SITE_URL

    def get_permalink(self):
        return self.get_site_url() + self.get_absolute_url()

    def __str__(self):
        return 'FeedItem'

    def is_post(self):
        return hasattr(self, 'post')

    def is_note(self):
        return hasattr(self, 'note')

    def get_child(self):
        if self.is_post():
            return self.post
        
        if self.is_note():
            return self.note

        return None
    
    def get_type_name(self):
        return self._meta.verbose_name
        
    def get_type_name_plural(self):
        return self._meta.verbose_name_plural
    
    def get_type_verb(self):
        return self._meta.object_verb

    def meta_template(self):
        return f'{ self._meta.app_label }/_meta.html'

    def feed_item_template(self):
        return None

    def feed_item_header(self):
        return None
    
    def feed_item_content(self):
        return None