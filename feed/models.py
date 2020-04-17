from django.db import models

# Create your models here.
class FeedItem(models.Model):
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

    class Meta:
        abstract = True

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, db_index=True, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('feed:tag', args=[self.id, self.slug])

    def test(self):
        return self.name