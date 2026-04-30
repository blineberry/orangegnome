from django.db import models
from feed.models import FeedItem
from django.urls import reverse
from django.core.exceptions import ValidationError

# Create your models here.
class Like(FeedItem):
    pass