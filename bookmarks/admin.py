from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea,TextInput
from .models import Bookmark
from feed.admin import SyndicatableAdmin
from base.widgets import PlainTextCountTextarea, PlainTextCountTextInput

# Register your models here.
# Customize the Admin form
class BookmarkModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    title = CharField(
        widget=PlainTextCountTextInput(max=Bookmark.title_max),
        required=False)
    #title = CharField(widget=TextInput)

    quote = CharField(
        widget=PlainTextCountTextarea(max=Bookmark.quote_max), 
        required=False)
    """Display the quote input as a Textarea"""

    commentary = CharField(
        widget=PlainTextCountTextarea(max=Bookmark.commentary_max), 
        required=False)
    """Display the commentary input as a Textarea"""

    class Meta:
        model = Bookmark
        fields = [
            'url',
            'title',
            'in_reply_to', 
            'quote',
            'commentary',
            'author',
            'tags',
            'syndicate_to_twitter', 
            'syndicated_to_twitter',
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

    readonly_fields = ('syndicated_to_twitter', 'syndicated_to_mastodon')
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('url', 'title', 'quote', 'commentary','in_reply_to','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_twitter', 'syndicated_to_twitter', 'syndicate_to_mastodon','syndicated_to_mastodon')
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

    list_display = ['url', 'title_plain']
    """The fields to display on the admin list view."""

# Register your models here.
admin.site.register(Bookmark, BookmarkAdmin)