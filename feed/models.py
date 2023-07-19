from django.db import models
from django.urls import reverse
from profiles.models import Profile
from django.conf import settings
from datetime import datetime
from django.utils import timezone

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

    def to_pascale_case(self, strip_special_characters = True):
        name = self.name

        if strip_special_characters:
            name = ''.join(filter(lambda character : character.isalnum() or character == ' ',self.name))

        return "".join(name.title().split())

    def to_hashtag(self, strip_special_characters = True):
        return "#" + self.to_pascale_case(strip_special_characters)

class FeedItem(models.Model):
    updated = models.DateTimeField(null=True)
    author = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True)
    published = models.DateTimeField(null=True,blank=True)
    tags = models.ManyToManyField(Tag, related_name='feed_items',blank=True)
    in_reply_to = models.CharField(max_length=2000, blank=True, null=True)

    postheader_template = "feed/_postheader_template.html"
    postcontent_template = "feed/_postbody_template.html"

    @staticmethod
    def get_site_url():
        return settings.SITE_URL
    
    def is_published(self):
        if self.published is None:
            return False
        
        if self.published > timezone.now():
            return False
        
        return True

    def get_permalink(self):
        return self.get_site_url() + self.get_absolute_url()

    def __str__(self):
        return 'FeedItem'

    def is_post(self):
        return hasattr(self, 'post')

    def is_note(self):
        return hasattr(self, 'note')

    def is_photo(self):
        return hasattr(self, 'photo')

    def is_exercise(self):
        return hasattr(self, 'exercise')

    def is_bookmark(self):
        return hasattr(self, 'bookmark')

    def get_child(self):
        if self.is_post():
            return self.post
        
        if self.is_note():
            return self.note

        if self.is_photo():
            return self.photo

        if self.is_exercise():
            return self.exercise
        
        if self.is_bookmark():
            return self.bookmark

        raise NotImplementedError
    
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
    
    def feed_item_link(self):
        return self.get_child().get_permalink()
    
    def get_edit_link(self):
        #print(self._meta.app_name)
        return reverse(f"admin:{self._meta.app_label}_{self._meta.model_name}_change", args=(self.pk,))