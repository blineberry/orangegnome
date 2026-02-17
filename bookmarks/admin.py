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
class BookmarkModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    title_md = CharField(
        widget=PlainTextCountTextInput(max=Bookmark.title_max),
        required=False)
    #title = CharField(widget=TextInput)

    quote_md = CharField(
        widget=PlainTextCountTextarea(max=Bookmark.quote_max), 
        required=False)
    """Display the quote input as a Textarea"""

    content_md = CharField(
        widget=PlainTextCountTextarea(max=Bookmark.content_max), 
        required=False)
    """Display the content input as a Textarea"""

    class Meta:
        model = Bookmark
        fields = [
            'url',
            'title_md',
            'in_reply_to', 
            'quote_md',
            'content_md',
            'author',
            'tags',
            'published'
        ]

# Admin specs for the Bookmark model
class BookmarkAdmin(SyndicatableAdmin):
    """
    Specifications for the Bookmark Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = BookmarkModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('syndicated_to_mastodon',)
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('url', 'title_md', 'quote_md', 'content_md','in_reply_to','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('published',)
        })
    )
    """
    Group related fields together. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.fieldsets
    """

    filter_horizontal = ('tags',)
    """
    Use the built-in interface for the tags many-to-many relationship.
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.filter_horizontal
    """

    list_display = ['url', 'title_txt']
    """The fields to display on the admin list view."""
       

# Register your models here.
admin.site.register(Bookmark, BookmarkAdmin)