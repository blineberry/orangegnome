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

    class Meta:
        abstract = True