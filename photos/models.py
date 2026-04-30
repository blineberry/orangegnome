"""
Implementation of the IndieWeb Photo post type.
https://indieweb.org/photo
"""

from django.db import models
from django.forms import ValidationError
from feed.fields import CommonmarkField
from feed.models import FeedItem
from django.urls import reverse
from .storage import PublicAzureStorage
from uuid import uuid4
from datetime import date
from django_resized import ResizedImageField
from django_resized.forms import ResizedImageFieldFile
from django.utils.html import mark_safe
from django.template.loader import render_to_string

# Custom upload_to callable
# Heavily influenced from https://stackoverflow.com/a/15141228/814492
def upload_to_callable(instance, filename):
    ext = filename.split('.')[-1]

    filename = '{}.{}'.format(uuid4().hex, ext)

    d = date.today()

    return '{0}/{1}'.format(d.strftime('%Y/%m/%d'),filename)





class OGResizedImageFieldFile(ResizedImageFieldFile):
    def save(self, name, content, save=True):
        super().save(name, content, save)
        self.field.update_dimension_fields(self.instance, force=True)

class OGResizedImageField(ResizedImageField):
    attr_class = OGResizedImageFieldFile

# Create your models here.
class Photo(FeedItem):
    """
    A Photo model.

    Implements MastodonSyndicatable and FeedItem.
    """