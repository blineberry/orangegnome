from django.contrib import admin
from django.forms import ModelForm, CharField, Textarea
from .models import Bookmark
from syndications.admin import SyndicatableAdmin
from feed.admin import PublishableAdmin
from webmentions.admin import WebmentionAdmin
from webmentions.models import Webmention

# Register your models here.
# Customize the Admin form
class BookmarkModelForm(ModelForm):
    """
    Customizations for the Add and Change admin pages.

    Inherits from forms.ModelForm.
    """

    quote = CharField(widget=Textarea, required=False)
    """Display the quote input as a Textarea"""

    commentary = CharField(widget=Textarea, required=False)
    """Display the commentary input as a Textarea"""

    class Meta:
        model = Bookmark
        fields = [
            'url',
            'title',
            'quote',
            'commentary',
            'author',
            'tags',
            'syndicate_to_twitter', 
            'syndicated_to_twitter',
            'is_published',
            'published'
        ]

# Admin specs for the Bookmark model
class BookmarkAdmin(PublishableAdmin, SyndicatableAdmin, WebmentionAdmin):
    """
    Specifications for the Bookmark Admin page.

    Inherits from PublishableAdmin, SyndicatableAdmin, and WebmentionAdmin
    """

    form = BookmarkModelForm
    """Override the dynamically created form with customizations."""

    readonly_fields = ('published','syndicated_to_twitter', 'syndicated_to_mastodon')
    """
    These fields will be shown but uneditable. 
    
    https://docs.djangoproject.com/en/4.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.readonly_fields
    """

    fieldsets = (
        (None, {
            'fields': ('url', 'title', 'quote', 'commentary','author','tags')
        }),
        ('Syndication', {
            'fields': ('syndicate_to_twitter', 'syndicated_to_twitter', 'syndicate_to_mastodon','syndicated_to_mastodon')
        }),
        ('Publishing', {
            'fields': ('is_published','published')
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

    list_display = ['url', 'title']
    """The fields to display on the admin list view."""

    def get_links_to_webmention(self, request, obj, form, change):
        """
        Called from save_model, returns a list of urls from the Bookmark caption.

        Has all the information available in save_model:
        request     =   the HttpRequest
        obj         =   the Bookmark instance
        form        =   the ModelForm instance
        change      =   boolean value based on whether the object is being added or 
                        changed
        """

        content_links = Webmention.get_links_from_text(obj.commentary)

        if change:
            old_obj = Bookmark.objects.get(id=obj.id)
            old_links = Webmention.get_links_from_text(old_obj.commentary)
            content_links = list(set(content_links + old_links))

        if obj.in_reply_to is not None:
            content_links.append(obj.in_reply_to)

        return content_links

    def should_send_webmentions(self, request, obj, form, change):
        """
        Given the save_model context, returns a boolean if webmentions should 
        be sent or not.
        """
        return obj.is_published

# Register your models here.
admin.site.register(Bookmark, BookmarkAdmin)