from django.db import models
from feed.models import FeedItem
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator
from django.template.loader import render_to_string

# Create your models here.
class Repost(FeedItem):
    pass