from django.contrib import admin
from django.forms import ModelForm, CharField
from .models import Bookmark
from feed.admin import SyndicatableAdmin
from feed.widgets import PlainTextCountTextarea, PlainTextCountTextInput
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.contrib import messages

# Register your models here.
# Customize the Admin form