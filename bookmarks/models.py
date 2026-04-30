"""
Implementation of the IndieWeb Bookmark post type.
https://indieweb.org/bookmark
"""

from django.db import models
from django.urls import reverse
from feed.models import FeedItem
from django.template.loader import render_to_string
from feed.fields import CommonmarkField, CommonmarkInlineField
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
class Bookmark(FeedItem):
    """
    The Django model representing the bookmark.
    """